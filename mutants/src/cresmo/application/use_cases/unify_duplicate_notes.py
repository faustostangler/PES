"""Stage 7 Use Case: Vault Entity Resolution & Duplicate Note Unification.

Detects duplicate entities in the Obsidian Second Brain vault using shared aliases,
cross-referencing title-to-alias mappings, and honorific normalization.
Non-destructively merges duplicate notes, rewrites inbound [[WikiLinks]] across the
entire vault and Maps of Content (MOCs), synchronizes _index.json, and cleans up
redundant files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from cresmo.application.ports import VaultRepositoryPort
from cresmo.domain.entities import AtomicNote
from cresmo.domain.value_objects import (
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass(frozen=True)
class DuplicateCluster:
    """Represents a set of duplicate notes resolved to a single canonical identity."""

    canonical_title: NoteTitle
    merged_titles: tuple[NoteTitle, ...]
    links_rewritten_count: int


@dataclass(frozen=True)
class DeduplicationReport:
    """Summary of the Stage 7 vault deduplication execution."""

    clusters: tuple[DuplicateCluster, ...]

    @property
    def duplicates_unified_count(self) -> int:
        return len(self.clusters)

    @property
    def total_links_rewritten(self) -> int:
        return sum(c.links_rewritten_count for c in self.clusters)
mutants_xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore


class UnifyDuplicateNotesUseCase:
    """Stage 7: Graph Entity Resolution and Duplicate Unification."""

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut)
    def __init__(self, vault_port: VaultRepositoryPort) -> None:
        self.vault_port = vault_port

    def xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_orig(self, vault_port: VaultRepositoryPort) -> None:
        self.vault_port = vault_port

    def xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_1(self, vault_port: VaultRepositoryPort) -> None:
        self.vault_port = None

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut)
    def _normalize_for_matching(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_orig(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_1(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = None
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_2(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.upper().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_3(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("XXdom XX", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_4(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("DOM ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_5(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "XXdona XX", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_6(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "DONA ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_7(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "XXd. XX", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_8(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "D. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_9(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "XXd XX"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_10(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "D "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_11(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(None):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_12(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = None
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_13(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                return
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_14(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(None, " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_15(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", None, cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_16(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", None).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_17(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(" ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_18(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_19(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", ).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_20(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"XX[\s\-_.,()]+XX", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_21(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", "XX XX", cleaned).strip()

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut)
    def _are_duplicates(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_orig(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_1(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.upper() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_2(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() != note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_3(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.upper():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_4(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return True

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_5(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = None
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_6(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.upper()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_7(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = None

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_8(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.upper()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_9(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = None
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_10(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.upper() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_11(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = None

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_12(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.upper() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_13(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b and t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_14(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a not in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_15(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b not in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_16(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return False

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_17(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = None
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_18(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a | aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_19(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return False

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_20(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = None
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_21(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(None)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_22(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = None
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_23(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(None)
        return norm_a == norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_24(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b or len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_25(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a != norm_b and len(norm_a) >= 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_26(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) > 4

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_27(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= 5

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut)
    def _merge_notes(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_orig(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_1(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = None
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_2(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.upper()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_3(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = None
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_4(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.upper() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_5(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() == canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_6(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(None)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_7(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.upper() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_8(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() == canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_9(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(None)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_10(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.upper() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_11(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() == canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_12(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(None)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_13(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = None

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_14(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(None)

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_15(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(None))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_16(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = None

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_17(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(None)

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_18(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(None))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_19(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) & set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_20(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(None) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_21(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(None)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_22(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = None
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_23(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.upper(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_24(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.upper()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_25(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = None
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_26(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.upper() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_27(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_28(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = None
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_29(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.upper()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_30(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.upper() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_31(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_32(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = None

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_33(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.upper()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_34(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = None

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_35(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(None)

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_36(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = None
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_37(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = None
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_38(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant and def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_39(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical != def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_40(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant not in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_41(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = None
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_42(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical not in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_43(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = None
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_44(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = None

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_45(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = None
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_46(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_47(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is not None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_48(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = None
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_49(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = None
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_50(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause and redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_51(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = None
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_52(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect and redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_53(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = None
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_54(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution and redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_55(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = None

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_56(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=None, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_57(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=None, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_58(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=None)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_59(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_60(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_61(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, )

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_62(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = None
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_63(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_64(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is not None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_65(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = None
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_66(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = None
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_67(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors and redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_68(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = None
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_69(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events and redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_70(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = None
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_71(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath and redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_72(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = None

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_73(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=None, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_74(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=None, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_75(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=None)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_76(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_77(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_78(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, )

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_79(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = None
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_80(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain and redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_81(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = None
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_82(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster and redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_83(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = None

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_84(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source and redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_85(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=None,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_86(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=None,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_87(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=None,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_88(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=None,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_89(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=None,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_90(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=None,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_91(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=None,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_92(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=None,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_93(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=None,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_94(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=None,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_95(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=None,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_96(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_97(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_98(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_99(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_100(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_101(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_102(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_103(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_104(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_105(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_106(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            )

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut)
    def execute(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_orig(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_1(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = None
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_2(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_3(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=None)

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_4(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = None
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_5(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = None

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_6(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(None):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_7(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = None
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_8(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = None
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_9(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.upper()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_10(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a not in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_11(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                break

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_12(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = None
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_13(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = None
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_14(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = None

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_15(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 1

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_16(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(None, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_17(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, None):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_18(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_19(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, ):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_20(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i - 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_21(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 2, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_22(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = None
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_23(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = None
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_24(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.upper()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_25(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b not in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_26(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    break

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_27(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(None, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_28(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, None):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_29(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_30(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, ):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_31(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) >= len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_32(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) - 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_33(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 51:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_34(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = None
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_35(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = None
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_36(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = None
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_37(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = None

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_38(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = None

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_39(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(None, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_40(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, None)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_41(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_42(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, )

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_43(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(None)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_44(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(None)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_45(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(None)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_46(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = None
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_47(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        None, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_48(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, None
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_49(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_50(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_51(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten = rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_52(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten -= rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_53(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(None)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_54(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(None)
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_55(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.upper())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_56(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = None

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_57(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(None)
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_58(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.upper())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_59(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    None
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_60(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=None,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_61(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=None,
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_62(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=None,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_63(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_64(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_65(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_66(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(None),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_67(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=None)

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_68(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(None))

mutants_xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut['xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated

mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_2'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_3'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_4'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_5'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_6'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_7'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_8'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_9'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_10'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_11'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_12'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_13'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_14'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_15'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_16'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_17'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_18'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_19'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_20'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_21'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_21 # type: ignore # mutmut generated

mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_2'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_3'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_4'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_5'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_6'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_7'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_8'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_9'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_10'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_11'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_12'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_13'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_14'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_15'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_16'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_17'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_18'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_19'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_20'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_21'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_21 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_22'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_22 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_23'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_23 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_24'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_24 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_25'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_25 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_26'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_26 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_27'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_27 # type: ignore # mutmut generated

mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_2'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_3'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_4'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_5'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_6'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_7'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_8'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_9'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_10'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_11'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_12'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_13'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_14'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_15'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_16'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_17'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_18'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_19'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_20'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_21'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_21 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_22'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_22 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_23'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_23 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_24'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_24 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_25'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_25 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_26'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_26 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_27'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_27 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_28'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_28 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_29'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_29 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_30'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_30 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_31'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_31 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_32'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_32 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_33'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_33 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_34'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_34 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_35'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_35 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_36'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_36 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_37'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_37 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_38'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_38 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_39'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_39 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_40'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_40 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_41'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_41 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_42'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_42 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_43'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_43 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_44'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_44 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_45'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_45 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_46'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_46 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_47'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_47 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_48'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_48 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_49'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_49 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_50'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_50 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_51'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_51 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_52'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_52 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_53'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_53 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_54'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_54 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_55'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_55 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_56'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_56 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_57'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_57 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_58'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_58 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_59'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_59 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_60'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_60 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_61'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_61 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_62'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_62 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_63'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_63 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_64'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_64 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_65'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_65 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_66'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_66 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_67'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_67 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_68'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_68 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_69'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_69 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_70'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_70 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_71'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_71 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_72'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_72 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_73'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_73 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_74'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_74 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_75'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_75 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_76'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_76 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_77'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_77 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_78'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_78 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_79'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_79 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_80'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_80 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_81'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_81 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_82'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_82 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_83'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_83 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_84'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_84 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_85'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_85 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_86'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_86 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_87'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_87 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_88'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_88 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_89'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_89 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_90'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_90 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_91'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_91 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_92'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_92 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_93'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_93 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_94'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_94 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_95'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_95 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_96'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_96 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_97'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_97 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_98'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_98 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_99'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_99 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_100'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_100 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_101'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_101 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_102'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_102 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_103'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_103 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_104'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_104 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_105'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_105 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_106'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_106 # type: ignore # mutmut generated

mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_2'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_3'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_4'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_5'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_6'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_7'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_8'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_9'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_10'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_11'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_12'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_13'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_14'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_15'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_16'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_17'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_18'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_19'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_20'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_21'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_21 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_22'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_22 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_23'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_23 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_24'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_24 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_25'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_25 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_26'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_26 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_27'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_27 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_28'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_28 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_29'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_29 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_30'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_30 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_31'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_31 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_32'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_32 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_33'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_33 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_34'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_34 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_35'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_35 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_36'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_36 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_37'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_37 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_38'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_38 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_39'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_39 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_40'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_40 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_41'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_41 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_42'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_42 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_43'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_43 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_44'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_44 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_45'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_45 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_46'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_46 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_47'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_47 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_48'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_48 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_49'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_49 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_50'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_50 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_51'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_51 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_52'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_52 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_53'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_53 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_54'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_54 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_55'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_55 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_56'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_56 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_57'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_57 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_58'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_58 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_59'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_59 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_60'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_60 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_61'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_61 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_62'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_62 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_63'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_63 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_64'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_64 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_65'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_65 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_66'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_66 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_67'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_67 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_68'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_68 # type: ignore # mutmut generated
