"""Domain Identity Value Objects (ChannelName, ChannelId, ContentId, SourceModality).

Conforms to:
- ADR-019: Zero Primitive Obsession
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- SPEC-003: §2 (Channel Sync Models & Normalization Rules)
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from enum import Enum

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.constants import (
    MAX_CHANNEL_ID_LENGTH,
    MAX_CHANNEL_NAME_LENGTH,
    MIN_CANONICAL_CHANNEL_ID_LENGTH,
    MIN_CHANNEL_ID_LENGTH,
)

_CONTENT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
_VIDEO_ID_REGEX = re.compile(
    r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/|/live/)([a-zA-Z0-9_-]{8,64})",
    re.IGNORECASE,
)
_CHANNEL_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{2,64}$")
_CHANNEL_URL_EXTRACTOR = re.compile(
    r"(?:/channel/|/user/|/c/|^)(UC[a-zA-Z0-9_-]{2,62})",
    re.IGNORECASE,
)
_CHANNEL_OR_PLAYLIST_URL_REGEX = re.compile(
    r"youtube\.com/(?:@|c/|channel/|user/|playlist\?list=)",
    re.IGNORECASE,
)


class SourceModality(str, Enum):
    """Discriminator for input batch source modality.

    Conforms to ADR-019 (Zero Primitive Obsession).
    """

    FILE = "file"
    URL = "url"


@dataclass(frozen=True)
class ChannelName:
    """Canonical domain Value Object representing a content creator or source channel.

    Conforms to ADR-019: Zero Primitive Obsession.

    Invariants:
        - Value must be non-empty and not whitespace.
        - Automatically trimmed of leading and trailing whitespace.
        - Maximum length of 120 characters.
        - Prohibits path traversal sequences ('..' or '/' or '\\').
    """

    value: str

    def __post_init__(self) -> None:
        val = self.value.strip()
        if not val:
            raise DomainValidationError("ChannelName cannot be empty or whitespace.")
        if len(val) > MAX_CHANNEL_NAME_LENGTH:
            raise DomainValidationError(
                f"ChannelName exceeds maximum length of {MAX_CHANNEL_NAME_LENGTH} characters: '{val[:30]}...'"
            )
        if ".." in val or "/" in val or "\\" in val:
            raise DomainValidationError(
                f"ChannelName cannot contain path traversal or separator characters: '{val}'"
            )
        object.__setattr__(self, "value", val)

    @classmethod
    def from_string(cls, raw: str | ChannelName) -> ChannelName:
        """Ergonomic conversion factory accepting str or existing ChannelName."""
        if isinstance(raw, cls):
            return raw
        return cls(value=str(raw))

    def __str__(self) -> str:
        return self.value

    def strip(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ChannelName):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.strip()
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ChannelId:
    """Canonical domain Value Object representing a YouTube or media platform channel identifier.

    Conforms to ADR-019: Zero Primitive Obsession.

    Invariants:
        - Value must be non-empty and not whitespace.
        - Automatically trimmed.
        - Length between 2 and 64 characters.
        - Strictly matches ^[a-zA-Z0-9_-]{2,64}$ (zero path traversal or whitespace).
    """

    value: str

    def __post_init__(self) -> None:
        val = self.value.strip()
        if not val:
            raise DomainValidationError("ChannelId cannot be empty or whitespace.")
        if len(val) > MAX_CHANNEL_ID_LENGTH:
            raise DomainValidationError(
                f"ChannelId exceeds maximum length of {MAX_CHANNEL_ID_LENGTH} characters: '{val[:30]}...' (length: {len(val)})"
            )
        if len(val) < MIN_CHANNEL_ID_LENGTH:
            raise DomainValidationError(
                f"ChannelId must have at least {MIN_CHANNEL_ID_LENGTH} characters: '{val}'"
            )
        if ".." in val or "/" in val or "\\" in val:
            raise DomainValidationError(
                f"ChannelId cannot contain path traversal characters: '{val}'"
            )
        if not _CHANNEL_ID_REGEX.match(val):
            raise DomainValidationError(
                f"ChannelId contains invalid characters: '{val}'. Expected ^[a-zA-Z0-9_-]{{2,64}}$"
            )
        object.__setattr__(self, "value", val)

    @classmethod
    def from_string(cls, raw: str | ChannelId) -> ChannelId:
        """Ergonomic conversion factory accepting str or existing ChannelId."""
        if isinstance(raw, cls):
            return raw
        return cls(value=str(raw).strip())

    @classmethod
    def from_url_or_token(cls, raw: str | ChannelId) -> ChannelId:
        """Extract canonical ChannelId from YouTube URL or token."""
        if isinstance(raw, cls):
            return raw
        token = str(raw).strip()
        m = _CHANNEL_URL_EXTRACTOR.search(token)
        if m:
            candidate = m.group(1).strip()
            if _CHANNEL_ID_REGEX.match(candidate):
                return cls(value=candidate)
        if _CHANNEL_ID_REGEX.match(token):
            return cls(value=token)
        raise DomainValidationError(
            f"Unable to extract valid ChannelId from '{raw}'. Expected YouTube channel URL or ^[a-zA-Z0-9_-]{{2,64}}$."
        )

    @classmethod
    def extract_from_text(cls, text: str) -> ChannelId | None:
        """Extract ChannelId from text or URL safely, returning None on failure."""
        if not text or not text.strip():
            return None
        try:
            return cls.from_url_or_token(text)
        except (DomainValidationError, ValueError, TypeError):
            return None

    @classmethod
    def is_channel_or_playlist_url(cls, url: str) -> bool:
        """Discriminator checking if a given URL is a YouTube channel or playlist link."""
        if not url:
            return False
        u = url.strip()
        u_lower = u.lower()
        if "watch?v=" in u_lower and "list=" not in u_lower:
            return False
        return bool(_CHANNEL_OR_PLAYLIST_URL_REGEX.search(u))

    @property
    def is_youtube_canonical(self) -> bool:
        """Check if this channel identifier follows canonical YouTube format (UC prefix)."""
        return self.value.startswith("UC") and len(self.value) >= MIN_CANONICAL_CHANNEL_ID_LENGTH

    @property
    def uploads_playlist_id(self) -> str | None:
        """Convert canonical YouTube channel ID (UC...) to its uploads playlist ID (UU...)."""
        if self.is_youtube_canonical:
            return "UU" + self.value[2:]
        return None

    @property
    def uploads_playlist_url(self) -> str | None:
        """Generate canonical YouTube uploads playlist URL."""
        pid = self.uploads_playlist_id
        if pid:
            return f"https://www.youtube.com/playlist?list={pid}"
        return None

    @property
    def canonical_url(self) -> str:
        """Generate canonical YouTube channel URL or return identity."""
        if self.is_youtube_canonical:
            return f"https://www.youtube.com/channel/{self.value}"
        return self.value

    def __str__(self) -> str:
        return self.value

    def strip(self) -> str:
        """String duck typing helper."""
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ChannelId):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.strip()
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ContentId:
    """Strongly-typed unique identifier for a raw media item or transcript.

    Invariants:
        Must be a non-empty string between 8 and 64 characters matching ^[a-zA-Z0-9_-]+$.
        Zero whitespace or shell/path traversal characters allowed.
    """

    value: str

    def __post_init__(self) -> None:
        val = self.value.strip()
        # Security invariant: prevent directory traversal or injection in identifiers
        if not val or not _CONTENT_ID_PATTERN.match(val):
            raise DomainValidationError(
                f"Invalid ContentId '{self.value}'. Must match ^[a-zA-Z0-9_-]{{8,64}}$ without whitespace."
            )
        object.__setattr__(self, "value", val)

    @classmethod
    def from_string(cls, raw: str | ContentId) -> ContentId:
        """Ergonomic conversion factory accepting str or existing ContentId."""
        if isinstance(raw, cls):
            return raw
        return cls(value=str(raw).strip())

    @classmethod
    def from_url_or_token(cls, raw: str | ContentId) -> ContentId:
        """Extract canonical ContentId from YouTube watch/short/embed URL or token."""
        if isinstance(raw, cls):
            return raw
        token = str(raw).strip()
        m = _VIDEO_ID_REGEX.search(token)
        if m:
            candidate = m.group(1).strip()
            if _CONTENT_ID_PATTERN.match(candidate):
                return cls(value=candidate)
        if _CONTENT_ID_PATTERN.match(token):
            return cls(value=token)
        raise DomainValidationError(
            f"Unable to extract valid ContentId from '{raw}'. Expected YouTube URL or ^[a-zA-Z0-9_-]{{8,64}}$."
        )

    @classmethod
    def extract_from_text(cls, text: str) -> ContentId | None:
        """Extract canonical ContentId from text or URL safely, returning None on failure."""
        if not text or not text.strip():
            return None
        try:
            return cls.from_url_or_token(text)
        except (DomainValidationError, ValueError, TypeError):
            return None

    def __str__(self) -> str:
        return self.value

    def strip(self) -> str:
        """String duck typing helper."""
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ContentId):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.strip()
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True, slots=True)
class Channel:
    """Canonical domain Value Object representing a content creator or source channel.

    Encapsulates channel identity, human-readable name, platform ID, category, and canonical URL.
    Conforms to ADR-019 (Zero Primitive Obsession) and ADR-032.
    """

    name: ChannelName
    id: ChannelId | None = None
    category: str = ""
    url: str | None = None

    def __init__(
        self,
        name: ChannelName | str,
        id: ChannelId | str | None = None,
        category: str = "",
        url: str | None = None,
    ) -> None:
        c_name = ChannelName.from_string(name) if isinstance(name, (ChannelName, str)) else name
        c_id = ChannelId.from_string(id) if isinstance(id, (ChannelId, str)) and id else None
        if not isinstance(c_name, ChannelName):
            raise DomainValidationError(f"Invalid channel name type: {type(name)}")
        if c_id is not None and not isinstance(c_id, ChannelId):
            raise DomainValidationError(f"Invalid channel id type: {type(id)}")

        object.__setattr__(self, "name", c_name)
        object.__setattr__(self, "id", c_id)
        object.__setattr__(self, "category", category.strip() if category else "")
        object.__setattr__(self, "url", url.strip() if url else None)

    @classmethod
    def from_name(
        cls,
        name: str | ChannelName,
        id: str | ChannelId | None = None,
        category: str = "",
        url: str | None = None,
    ) -> Channel:
        """Ergonomic factory constructing Channel from primitive strings or Value Objects."""
        c_name = ChannelName.from_string(name)
        c_id = ChannelId.from_string(id) if id else None
        return cls(name=c_name, id=c_id, category=category, url=url)

    @property
    def tenant_key(self) -> str:
        """Canonical tenant format key ('channel:{token}')."""
        token = self.id.value if self.id else self.name.value
        return f"channel:{token}"

    @property
    def canonical_url(self) -> str:
        """Derive the canonical public URL for this channel."""
        if self.url:
            return self.url
        if self.id and self.id.is_youtube_canonical:
            return self.id.canonical_url
        return f"https://www.youtube.com/@{self.name.value}"

    def __str__(self) -> str:
        return self.name.value


@dataclass(frozen=True, slots=True)
class Content:
    """Canonical domain Value Object representing a media item, transcript, or video.

    Encapsulates content identifier, title, source URL, input modality, and publication date.
    Conforms to ADR-019 (Zero Primitive Obsession) and ADR-032.
    """

    id: ContentId
    title: str = ""
    url: str = ""
    modality: SourceModality = SourceModality.URL
    publication_date: datetime.date | None = None

    def __init__(
        self,
        id: ContentId | str,
        title: str = "",
        url: str = "",
        modality: SourceModality | str = SourceModality.URL,
        publication_date: datetime.date | None = None,
    ) -> None:
        c_id = ContentId.from_string(id) if isinstance(id, (ContentId, str)) else id
        if not isinstance(c_id, ContentId):
            raise DomainValidationError(f"Invalid content id type: {type(id)}")

        mod = SourceModality(modality.lower()) if isinstance(modality, str) else modality

        object.__setattr__(self, "id", c_id)
        object.__setattr__(self, "title", title.strip() if title else "")
        object.__setattr__(self, "url", url.strip() if url else "")
        object.__setattr__(self, "modality", mod)
        object.__setattr__(self, "publication_date", publication_date)

    @classmethod
    def create(
        cls,
        id: str | ContentId,
        title: str = "",
        url: str = "",
        modality: SourceModality | str = SourceModality.URL,
        publication_date: datetime.date | None = None,
    ) -> Content:
        """Ergonomic factory constructing Content from primitive strings or Value Objects."""
        c_id = ContentId.from_string(id)
        mod = SourceModality(modality.lower()) if isinstance(modality, str) else modality
        return cls(
            id=c_id,
            title=title,
            url=url,
            modality=mod,
            publication_date=publication_date,
        )

    @property
    def display_title(self) -> str:
        """Human-readable display title, falling back to canonical content identifier."""
        return self.title or self.id.value

    def __str__(self) -> str:
        return self.id.value


Video = Content
