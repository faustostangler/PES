"""Mock in-memory adapters for hermetic unit testing of Cresmo use cases.

Zero I/O, deterministic responses, capturing call histories for test assertions.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from cresmo.application.ports import (
    LedgerRepositoryPort,
    LLMTransformationPort,
    MediaIngestionPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    RawTranscript,
)
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ContentId,
    DiscoveredMediaItem,
    LedgerEntry,
    NoteTitle,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁMockMediaIngestionPortǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMockMediaIngestionPortǁingest_single_video__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut: MutantDict = {}  # type: ignore


class MockMediaIngestionPort(MediaIngestionPort):
    """In-memory mock for MediaIngestionPort."""

    @_mutmut_mutated(mutants_xǁMockMediaIngestionPortǁ__init____mutmut)
    def __init__(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = canned_transcript
        self.canned_feed = canned_feed or []
        self.ingest_single_calls: list[str] = []
        self.ingest_channels_calls: list[list[str]] = []
        self.discover_calls: list[ChannelFeedQuery] = []

    def xǁMockMediaIngestionPortǁ__init____mutmut_orig(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = canned_transcript
        self.canned_feed = canned_feed or []
        self.ingest_single_calls: list[str] = []
        self.ingest_channels_calls: list[list[str]] = []
        self.discover_calls: list[ChannelFeedQuery] = []

    def xǁMockMediaIngestionPortǁ__init____mutmut_1(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = None
        self.canned_feed = canned_feed or []
        self.ingest_single_calls: list[str] = []
        self.ingest_channels_calls: list[list[str]] = []
        self.discover_calls: list[ChannelFeedQuery] = []

    def xǁMockMediaIngestionPortǁ__init____mutmut_2(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = canned_transcript
        self.canned_feed = None
        self.ingest_single_calls: list[str] = []
        self.ingest_channels_calls: list[list[str]] = []
        self.discover_calls: list[ChannelFeedQuery] = []

    def xǁMockMediaIngestionPortǁ__init____mutmut_3(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = canned_transcript
        self.canned_feed = canned_feed and []
        self.ingest_single_calls: list[str] = []
        self.ingest_channels_calls: list[list[str]] = []
        self.discover_calls: list[ChannelFeedQuery] = []

    def xǁMockMediaIngestionPortǁ__init____mutmut_4(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = canned_transcript
        self.canned_feed = canned_feed or []
        self.ingest_single_calls: list[str] = None
        self.ingest_channels_calls: list[list[str]] = []
        self.discover_calls: list[ChannelFeedQuery] = []

    def xǁMockMediaIngestionPortǁ__init____mutmut_5(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = canned_transcript
        self.canned_feed = canned_feed or []
        self.ingest_single_calls: list[str] = []
        self.ingest_channels_calls: list[list[str]] = None
        self.discover_calls: list[ChannelFeedQuery] = []

    def xǁMockMediaIngestionPortǁ__init____mutmut_6(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = canned_transcript
        self.canned_feed = canned_feed or []
        self.ingest_single_calls: list[str] = []
        self.ingest_channels_calls: list[list[str]] = []
        self.discover_calls: list[ChannelFeedQuery] = None

    @_mutmut_mutated(mutants_xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut)
    def discover_channel_feed(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        self.discover_calls.append(query)
        return list(self.canned_feed)

    def xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut_orig(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        self.discover_calls.append(query)
        return list(self.canned_feed)

    def xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut_1(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        self.discover_calls.append(None)
        return list(self.canned_feed)

    def xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut_2(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        self.discover_calls.append(query)
        return list(None)

    @_mutmut_mutated(mutants_xǁMockMediaIngestionPortǁingest_single_video__mutmut)
    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        self.ingest_single_calls.append(video_url)
        return self.canned_transcript

    def xǁMockMediaIngestionPortǁingest_single_video__mutmut_orig(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        self.ingest_single_calls.append(video_url)
        return self.canned_transcript

    def xǁMockMediaIngestionPortǁingest_single_video__mutmut_1(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "XXbaseXX",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        self.ingest_single_calls.append(video_url)
        return self.canned_transcript

    def xǁMockMediaIngestionPortǁingest_single_video__mutmut_2(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "BASE",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        self.ingest_single_calls.append(video_url)
        return self.canned_transcript

    def xǁMockMediaIngestionPortǁingest_single_video__mutmut_3(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = True,
    ) -> RawTranscript | None:
        self.ingest_single_calls.append(video_url)
        return self.canned_transcript

    def xǁMockMediaIngestionPortǁingest_single_video__mutmut_4(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        self.ingest_single_calls.append(None)
        return self.canned_transcript

    @_mutmut_mutated(mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut)
    def ingest_channels_and_playlists(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(playlist_urls)
        return [self.canned_transcript] if self.canned_transcript else []

    def xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_orig(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(playlist_urls)
        return [self.canned_transcript] if self.canned_transcript else []

    def xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_1(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 731,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(playlist_urls)
        return [self.canned_transcript] if self.canned_transcript else []

    def xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_2(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "XXbaseXX",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(playlist_urls)
        return [self.canned_transcript] if self.canned_transcript else []

    def xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_3(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "BASE",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(playlist_urls)
        return [self.canned_transcript] if self.canned_transcript else []

    def xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_4(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = True,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(playlist_urls)
        return [self.canned_transcript] if self.canned_transcript else []

    def xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_5(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 5,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(playlist_urls)
        return [self.canned_transcript] if self.canned_transcript else []

    def xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_6(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(None)
        return [self.canned_transcript] if self.canned_transcript else []

    @_mutmut_mutated(mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut)
    def extract_channel_url_from_video(
        self,
        video_url: str,
    ) -> str | None:
        return getattr(self, "canned_channel_url", None)

    def xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_orig(
        self,
        video_url: str,
    ) -> str | None:
        return getattr(self, "canned_channel_url", None)

    def xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_1(
        self,
        video_url: str,
    ) -> str | None:
        return getattr(None, "canned_channel_url", None)

    def xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_2(
        self,
        video_url: str,
    ) -> str | None:
        return getattr(self, None, None)

    def xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_3(
        self,
        video_url: str,
    ) -> str | None:
        return getattr("canned_channel_url", None)

    def xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_4(
        self,
        video_url: str,
    ) -> str | None:
        return getattr(self, None)

    def xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_5(
        self,
        video_url: str,
    ) -> str | None:
        return getattr(self, "canned_channel_url", )

    def xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_6(
        self,
        video_url: str,
    ) -> str | None:
        return getattr(self, "XXcanned_channel_urlXX", None)

    def xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_7(
        self,
        video_url: str,
    ) -> str | None:
        return getattr(self, "CANNED_CHANNEL_URL", None)

mutants_xǁMockMediaIngestionPortǁ__init____mutmut['_mutmut_orig'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁ__init____mutmut['xǁMockMediaIngestionPortǁ__init____mutmut_1'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁ__init____mutmut['xǁMockMediaIngestionPortǁ__init____mutmut_2'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁ__init____mutmut['xǁMockMediaIngestionPortǁ__init____mutmut_3'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁ__init____mutmut['xǁMockMediaIngestionPortǁ__init____mutmut_4'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁ__init____mutmut['xǁMockMediaIngestionPortǁ__init____mutmut_5'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁ__init____mutmut['xǁMockMediaIngestionPortǁ__init____mutmut_6'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁ__init____mutmut_6 # type: ignore # mutmut generated

mutants_xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut['_mutmut_orig'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut['xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut_1'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut['xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut_2'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁdiscover_channel_feed__mutmut_2 # type: ignore # mutmut generated

mutants_xǁMockMediaIngestionPortǁingest_single_video__mutmut['_mutmut_orig'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_single_video__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_single_video__mutmut['xǁMockMediaIngestionPortǁingest_single_video__mutmut_1'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_single_video__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_single_video__mutmut['xǁMockMediaIngestionPortǁingest_single_video__mutmut_2'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_single_video__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_single_video__mutmut['xǁMockMediaIngestionPortǁingest_single_video__mutmut_3'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_single_video__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_single_video__mutmut['xǁMockMediaIngestionPortǁingest_single_video__mutmut_4'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_single_video__mutmut_4 # type: ignore # mutmut generated

mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut['_mutmut_orig'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut['xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_1'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut['xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_2'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut['xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_3'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut['xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_4'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut['xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_5'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut['xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_6'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁingest_channels_and_playlists__mutmut_6 # type: ignore # mutmut generated

mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut['_mutmut_orig'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut['xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_1'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut['xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_2'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut['xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_3'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut['xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_4'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut['xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_5'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut['xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_6'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_6 # type: ignore # mutmut generated
mutants_xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut['xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_7'] = MockMediaIngestionPort.xǁMockMediaIngestionPortǁextract_channel_url_from_video__mutmut_7 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁMockLLMAdapterǁtransform__mutmut: MutantDict = {}  # type: ignore


class MockLLMAdapter(LLMTransformationPort):
    """In-memory mock for LLMTransformationPort."""

    @_mutmut_mutated(mutants_xǁMockLLMAdapterǁ__init____mutmut)
    def __init__(self, responses: list[str] | None = None) -> None:
        self.responses = list(responses or [])
        self.call_history: list[dict[str, Any]] = []

    def xǁMockLLMAdapterǁ__init____mutmut_orig(self, responses: list[str] | None = None) -> None:
        self.responses = list(responses or [])
        self.call_history: list[dict[str, Any]] = []

    def xǁMockLLMAdapterǁ__init____mutmut_1(self, responses: list[str] | None = None) -> None:
        self.responses = None
        self.call_history: list[dict[str, Any]] = []

    def xǁMockLLMAdapterǁ__init____mutmut_2(self, responses: list[str] | None = None) -> None:
        self.responses = list(None)
        self.call_history: list[dict[str, Any]] = []

    def xǁMockLLMAdapterǁ__init____mutmut_3(self, responses: list[str] | None = None) -> None:
        self.responses = list(responses and [])
        self.call_history: list[dict[str, Any]] = []

    def xǁMockLLMAdapterǁ__init____mutmut_4(self, responses: list[str] | None = None) -> None:
        self.responses = list(responses or [])
        self.call_history: list[dict[str, Any]] = None

    @_mutmut_mutated(mutants_xǁMockLLMAdapterǁtransform__mutmut)
    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_orig(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_1(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            None
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_2(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "XXpromptXX": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_3(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "PROMPT": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_4(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "XXsystem_instructionXX": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_5(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "SYSTEM_INSTRUCTION": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_6(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "XXtemperatureXX": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_7(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "TEMPERATURE": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_8(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(None)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_9(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(1)
        return "Deterministic mock LLM response."

    def xǁMockLLMAdapterǁtransform__mutmut_10(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "XXDeterministic mock LLM response.XX"

    def xǁMockLLMAdapterǁtransform__mutmut_11(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "deterministic mock llm response."

    def xǁMockLLMAdapterǁtransform__mutmut_12(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "DETERMINISTIC MOCK LLM RESPONSE."

mutants_xǁMockLLMAdapterǁ__init____mutmut['_mutmut_orig'] = MockLLMAdapter.xǁMockLLMAdapterǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁ__init____mutmut['xǁMockLLMAdapterǁ__init____mutmut_1'] = MockLLMAdapter.xǁMockLLMAdapterǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁ__init____mutmut['xǁMockLLMAdapterǁ__init____mutmut_2'] = MockLLMAdapter.xǁMockLLMAdapterǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁ__init____mutmut['xǁMockLLMAdapterǁ__init____mutmut_3'] = MockLLMAdapter.xǁMockLLMAdapterǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁ__init____mutmut['xǁMockLLMAdapterǁ__init____mutmut_4'] = MockLLMAdapter.xǁMockLLMAdapterǁ__init____mutmut_4 # type: ignore # mutmut generated

mutants_xǁMockLLMAdapterǁtransform__mutmut['_mutmut_orig'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_1'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_2'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_3'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_4'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_5'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_6'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_6 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_7'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_7 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_8'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_8 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_9'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_9 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_10'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_10 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_11'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_11 # type: ignore # mutmut generated
mutants_xǁMockLLMAdapterǁtransform__mutmut['xǁMockLLMAdapterǁtransform__mutmut_12'] = MockLLMAdapter.xǁMockLLMAdapterǁtransform__mutmut_12 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁremove_index_entry__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut: MutantDict = {}  # type: ignore


class InMemoryVaultAdapter(VaultRepositoryPort):
    """In-memory mock for VaultRepositoryPort."""

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁ__init____mutmut)
    def __init__(self) -> None:
        self.raw_transcripts: dict[str, RawTranscript] = {}
        self.compendiums: dict[str, EnrichedCompendium] = {}
        self.atomic_notes: dict[str, AtomicNote] = {}
        self.index_entries: dict[str, dict[str, Any]] = {}
        self.mocs: dict[str, MapOfContent] = {}

    def xǁInMemoryVaultAdapterǁ__init____mutmut_orig(self) -> None:
        self.raw_transcripts: dict[str, RawTranscript] = {}
        self.compendiums: dict[str, EnrichedCompendium] = {}
        self.atomic_notes: dict[str, AtomicNote] = {}
        self.index_entries: dict[str, dict[str, Any]] = {}
        self.mocs: dict[str, MapOfContent] = {}

    def xǁInMemoryVaultAdapterǁ__init____mutmut_1(self) -> None:
        self.raw_transcripts: dict[str, RawTranscript] = None
        self.compendiums: dict[str, EnrichedCompendium] = {}
        self.atomic_notes: dict[str, AtomicNote] = {}
        self.index_entries: dict[str, dict[str, Any]] = {}
        self.mocs: dict[str, MapOfContent] = {}

    def xǁInMemoryVaultAdapterǁ__init____mutmut_2(self) -> None:
        self.raw_transcripts: dict[str, RawTranscript] = {}
        self.compendiums: dict[str, EnrichedCompendium] = None
        self.atomic_notes: dict[str, AtomicNote] = {}
        self.index_entries: dict[str, dict[str, Any]] = {}
        self.mocs: dict[str, MapOfContent] = {}

    def xǁInMemoryVaultAdapterǁ__init____mutmut_3(self) -> None:
        self.raw_transcripts: dict[str, RawTranscript] = {}
        self.compendiums: dict[str, EnrichedCompendium] = {}
        self.atomic_notes: dict[str, AtomicNote] = None
        self.index_entries: dict[str, dict[str, Any]] = {}
        self.mocs: dict[str, MapOfContent] = {}

    def xǁInMemoryVaultAdapterǁ__init____mutmut_4(self) -> None:
        self.raw_transcripts: dict[str, RawTranscript] = {}
        self.compendiums: dict[str, EnrichedCompendium] = {}
        self.atomic_notes: dict[str, AtomicNote] = {}
        self.index_entries: dict[str, dict[str, Any]] = None
        self.mocs: dict[str, MapOfContent] = {}

    def xǁInMemoryVaultAdapterǁ__init____mutmut_5(self) -> None:
        self.raw_transcripts: dict[str, RawTranscript] = {}
        self.compendiums: dict[str, EnrichedCompendium] = {}
        self.atomic_notes: dict[str, AtomicNote] = {}
        self.index_entries: dict[str, dict[str, Any]] = {}
        self.mocs: dict[str, MapOfContent] = None

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut)
    def save_raw_transcript(self, transcript: RawTranscript) -> None:
        self.raw_transcripts[transcript.content_id.value] = transcript

    def xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut_orig(self, transcript: RawTranscript) -> None:
        self.raw_transcripts[transcript.content_id.value] = transcript

    def xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut_1(self, transcript: RawTranscript) -> None:
        self.raw_transcripts[transcript.content_id.value] = None

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut)
    def get_raw_transcript(self, content_id: ContentId) -> RawTranscript | None:
        return self.raw_transcripts.get(content_id.value)

    def xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut_orig(self, content_id: ContentId) -> RawTranscript | None:
        return self.raw_transcripts.get(content_id.value)

    def xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut_1(self, content_id: ContentId) -> RawTranscript | None:
        return self.raw_transcripts.get(None)

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut)
    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        self.compendiums[compendium.content_id.value] = compendium

    def xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut_orig(self, compendium: EnrichedCompendium) -> None:
        self.compendiums[compendium.content_id.value] = compendium

    def xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut_1(self, compendium: EnrichedCompendium) -> None:
        self.compendiums[compendium.content_id.value] = None

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut)
    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        return self.compendiums.get(content_id.value)

    def xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut_orig(self, content_id: ContentId) -> EnrichedCompendium | None:
        return self.compendiums.get(content_id.value)

    def xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut_1(self, content_id: ContentId) -> EnrichedCompendium | None:
        return self.compendiums.get(None)

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut)
    def save_atomic_note(self, note: AtomicNote) -> None:
        self.atomic_notes[note.title.value.lower()] = note

    def xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut_orig(self, note: AtomicNote) -> None:
        self.atomic_notes[note.title.value.lower()] = note

    def xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut_1(self, note: AtomicNote) -> None:
        self.atomic_notes[note.title.value.lower()] = None

    def xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut_2(self, note: AtomicNote) -> None:
        self.atomic_notes[note.title.value.upper()] = note

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut)
    def get_atomic_note_by_title(self, title: NoteTitle) -> AtomicNote | None:
        return self.atomic_notes.get(title.value.lower())

    def xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut_orig(self, title: NoteTitle) -> AtomicNote | None:
        return self.atomic_notes.get(title.value.lower())

    def xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut_1(self, title: NoteTitle) -> AtomicNote | None:
        return self.atomic_notes.get(None)

    def xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut_2(self, title: NoteTitle) -> AtomicNote | None:
        return self.atomic_notes.get(title.value.upper())

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut)
    def get_all_atomic_notes(self) -> list[AtomicNote]:
        return list(self.atomic_notes.values())

    def xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut_orig(self) -> list[AtomicNote]:
        return list(self.atomic_notes.values())

    def xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut_1(self) -> list[AtomicNote]:
        return list(None)

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut)
    def update_index_entry(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_orig(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_1(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = None

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_2(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.upper()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_3(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "XXtitleXX": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_4(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "TITLE": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_5(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "XXtypeXX": note.note_type.value,
            "domain": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_6(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "TYPE": note.note_type.value,
            "domain": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_7(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "XXdomainXX": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_8(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "DOMAIN": note.domain,
            "aliases": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_9(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "XXaliasesXX": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_10(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "ALIASES": list(note.aliases),
        }

    def xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_11(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "aliases": list(None),
        }

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut)
    def save_map_of_content(self, moc: MapOfContent) -> None:
        self.mocs[moc.title.value.lower()] = moc

    def xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut_orig(self, moc: MapOfContent) -> None:
        self.mocs[moc.title.value.lower()] = moc

    def xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut_1(self, moc: MapOfContent) -> None:
        self.mocs[moc.title.value.lower()] = None

    def xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut_2(self, moc: MapOfContent) -> None:
        self.mocs[moc.title.value.upper()] = moc

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut)
    def delete_atomic_note(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(note.title.value.lower(), None)
        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_orig(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(note.title.value.lower(), None)
        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_1(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(None, None)
        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_2(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(None)
        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_3(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(note.title.value.lower(), )
        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_4(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(note.title.value.upper(), None)
        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_5(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(note.title.value.lower(), None)
        self.remove_index_entry(None)
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_6(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(note.title.value.lower(), None)
        self.remove_index_entry(note.title.value.upper())
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_7(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(note.title.value.lower(), None)
        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(None)

    def xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_8(self, note: AtomicNote) -> None:
        self.atomic_notes.pop(note.title.value.lower(), None)
        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(alias.upper())

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁremove_index_entry__mutmut)
    def remove_index_entry(self, key: str) -> None:
        self.index_entries.pop(key.lower().strip(), None)

    def xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_orig(self, key: str) -> None:
        self.index_entries.pop(key.lower().strip(), None)

    def xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_1(self, key: str) -> None:
        self.index_entries.pop(None, None)

    def xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_2(self, key: str) -> None:
        self.index_entries.pop(None)

    def xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_3(self, key: str) -> None:
        self.index_entries.pop(key.lower().strip(), )

    def xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_4(self, key: str) -> None:
        self.index_entries.pop(key.upper().strip(), None)

    @_mutmut_mutated(mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut)
    def rewrite_wiki_links(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_orig(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_1(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = None
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_2(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = None
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_3(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.upper() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_4(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() != new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_5(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.upper():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_6(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 1
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_7(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = None
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_8(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(None, re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_9(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", None)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_10(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_11(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", )
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_12(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(None)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_13(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = None
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_14(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 1
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_15(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(None):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_16(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = None
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_17(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                None
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_18(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.upper() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_19(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() != old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_20(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.upper() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_21(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = None
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_22(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(None, note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_23(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", None)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_24(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_25(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", )
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_26(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 and new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_27(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count >= 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_28(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 1 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_29(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels == note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_30(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = None
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_31(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=None,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_32(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=None,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_33(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=None,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_34(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=None,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_35(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=None,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_36(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=None,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_37(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=None,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_38(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=None,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_39(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=None,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_40(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=None,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_41(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=None,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_42(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_43(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_44(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_45(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_46(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_47(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_48(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_49(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_50(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_51(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    cross_context=note.cross_context,
                )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_52(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    )
                updated += 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_53(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated = 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_54(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated -= 1
        return updated

    def xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_55(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0
        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated = 0
        for k, note in list(self.atomic_notes.items()):
            new_rels = tuple(
                new_title if r.value.lower() == old_val.lower() else r
                for r in note.direct_relations
            )
            new_def, count = pattern.subn(rf"[[{new_val}\1]]", note.definition)
            if count > 0 or new_rels != note.direct_relations:
                self.atomic_notes[k] = AtomicNote(
                    title=note.title,
                    note_type=note.note_type,
                    definition=new_def,
                    content_tags=note.content_tags,
                    domain=note.domain,
                    cluster=note.cluster,
                    source=note.source,
                    aliases=note.aliases,
                    direct_relations=new_rels,
                    causal_matrix=note.causal_matrix,
                    cross_context=note.cross_context,
                )
                updated += 2
        return updated

mutants_xǁInMemoryVaultAdapterǁ__init____mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁ__init____mutmut['xǁInMemoryVaultAdapterǁ__init____mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁ__init____mutmut['xǁInMemoryVaultAdapterǁ__init____mutmut_2'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁ__init____mutmut['xǁInMemoryVaultAdapterǁ__init____mutmut_3'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁ__init____mutmut['xǁInMemoryVaultAdapterǁ__init____mutmut_4'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁ__init____mutmut['xǁInMemoryVaultAdapterǁ__init____mutmut_5'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁ__init____mutmut_5 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut['xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_raw_transcript__mutmut_1 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut['xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_raw_transcript__mutmut_1 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut['xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_enriched_compendium__mutmut_1 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut['xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_enriched_compendium__mutmut_1 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut['xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut['xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut_2'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_atomic_note__mutmut_2 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut['xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut['xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut_2'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_atomic_note_by_title__mutmut_2 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut['xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁget_all_atomic_notes__mutmut_1 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_2'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_2 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_3'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_3 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_4'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_4 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_5'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_5 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_6'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_6 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_7'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_7 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_8'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_8 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_9'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_9 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_10'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_10 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut['xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_11'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁupdate_index_entry__mutmut_11 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut['xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut['xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut_2'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁsave_map_of_content__mutmut_2 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_2'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_2 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_3'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_3 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_4'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_4 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_5'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_5 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_6'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_6 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_7'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_7 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut['xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_8'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁdelete_atomic_note__mutmut_8 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁremove_index_entry__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁremove_index_entry__mutmut['xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁremove_index_entry__mutmut['xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_2'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_2 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁremove_index_entry__mutmut['xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_3'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_3 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁremove_index_entry__mutmut['xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_4'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁremove_index_entry__mutmut_4 # type: ignore # mutmut generated

mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['_mutmut_orig'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_1'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_2'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_2 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_3'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_3 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_4'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_4 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_5'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_5 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_6'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_6 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_7'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_7 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_8'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_8 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_9'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_9 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_10'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_10 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_11'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_11 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_12'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_12 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_13'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_13 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_14'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_14 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_15'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_15 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_16'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_16 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_17'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_17 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_18'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_18 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_19'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_19 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_20'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_20 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_21'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_21 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_22'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_22 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_23'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_23 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_24'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_24 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_25'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_25 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_26'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_26 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_27'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_27 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_28'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_28 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_29'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_29 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_30'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_30 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_31'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_31 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_32'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_32 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_33'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_33 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_34'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_34 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_35'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_35 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_36'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_36 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_37'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_37 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_38'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_38 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_39'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_39 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_40'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_40 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_41'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_41 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_42'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_42 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_43'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_43 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_44'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_44 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_45'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_45 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_46'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_46 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_47'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_47 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_48'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_48 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_49'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_49 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_50'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_50 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_51'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_51 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_52'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_52 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_53'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_53 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_54'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_54 # type: ignore # mutmut generated
mutants_xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut['xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_55'] = InMemoryVaultAdapter.xǁInMemoryVaultAdapterǁrewrite_wiki_links__mutmut_55 # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryLedgerAdapterǁis_processed__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryLedgerAdapterǁmark_processed__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryLedgerAdapterǁsave_entry__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryLedgerAdapterǁget_entry__mutmut: MutantDict = {}  # type: ignore
mutants_xǁInMemoryLedgerAdapterǁlist_entries__mutmut: MutantDict = {}  # type: ignore


class InMemoryLedgerAdapter(LedgerRepositoryPort):
    """In-memory mock for LedgerRepositoryPort."""

    @_mutmut_mutated(mutants_xǁInMemoryLedgerAdapterǁ__init____mutmut)
    def __init__(self) -> None:
        self.processed_ids: set[str] = set()
        self.entries: dict[str, LedgerEntry] = {}

    def xǁInMemoryLedgerAdapterǁ__init____mutmut_orig(self) -> None:
        self.processed_ids: set[str] = set()
        self.entries: dict[str, LedgerEntry] = {}

    def xǁInMemoryLedgerAdapterǁ__init____mutmut_1(self) -> None:
        self.processed_ids: set[str] = None
        self.entries: dict[str, LedgerEntry] = {}

    def xǁInMemoryLedgerAdapterǁ__init____mutmut_2(self) -> None:
        self.processed_ids: set[str] = set()
        self.entries: dict[str, LedgerEntry] = None

    @_mutmut_mutated(mutants_xǁInMemoryLedgerAdapterǁis_processed__mutmut)
    def is_processed(self, content_id: ContentId) -> bool:
        return content_id.value in self.processed_ids

    def xǁInMemoryLedgerAdapterǁis_processed__mutmut_orig(self, content_id: ContentId) -> bool:
        return content_id.value in self.processed_ids

    def xǁInMemoryLedgerAdapterǁis_processed__mutmut_1(self, content_id: ContentId) -> bool:
        return content_id.value not in self.processed_ids

    @_mutmut_mutated(mutants_xǁInMemoryLedgerAdapterǁmark_processed__mutmut)
    def mark_processed(self, content_id: ContentId) -> None:
        self.processed_ids.add(content_id.value)

    def xǁInMemoryLedgerAdapterǁmark_processed__mutmut_orig(self, content_id: ContentId) -> None:
        self.processed_ids.add(content_id.value)

    def xǁInMemoryLedgerAdapterǁmark_processed__mutmut_1(self, content_id: ContentId) -> None:
        self.processed_ids.add(None)

    @_mutmut_mutated(mutants_xǁInMemoryLedgerAdapterǁsave_entry__mutmut)
    def save_entry(self, entry: LedgerEntry) -> None:
        self.processed_ids.add(entry.content_id.value)
        self.entries[entry.content_id.value] = entry

    def xǁInMemoryLedgerAdapterǁsave_entry__mutmut_orig(self, entry: LedgerEntry) -> None:
        self.processed_ids.add(entry.content_id.value)
        self.entries[entry.content_id.value] = entry

    def xǁInMemoryLedgerAdapterǁsave_entry__mutmut_1(self, entry: LedgerEntry) -> None:
        self.processed_ids.add(None)
        self.entries[entry.content_id.value] = entry

    def xǁInMemoryLedgerAdapterǁsave_entry__mutmut_2(self, entry: LedgerEntry) -> None:
        self.processed_ids.add(entry.content_id.value)
        self.entries[entry.content_id.value] = None

    @_mutmut_mutated(mutants_xǁInMemoryLedgerAdapterǁget_entry__mutmut)
    def get_entry(self, content_id: ContentId) -> LedgerEntry | None:
        return self.entries.get(content_id.value)

    def xǁInMemoryLedgerAdapterǁget_entry__mutmut_orig(self, content_id: ContentId) -> LedgerEntry | None:
        return self.entries.get(content_id.value)

    def xǁInMemoryLedgerAdapterǁget_entry__mutmut_1(self, content_id: ContentId) -> LedgerEntry | None:
        return self.entries.get(None)

    @_mutmut_mutated(mutants_xǁInMemoryLedgerAdapterǁlist_entries__mutmut)
    def list_entries(self, limit: int = 100, offset: int = 0) -> list[LedgerEntry]:
        return list(self.entries.values())[offset : offset + limit]

    def xǁInMemoryLedgerAdapterǁlist_entries__mutmut_orig(self, limit: int = 100, offset: int = 0) -> list[LedgerEntry]:
        return list(self.entries.values())[offset : offset + limit]

    def xǁInMemoryLedgerAdapterǁlist_entries__mutmut_1(self, limit: int = 101, offset: int = 0) -> list[LedgerEntry]:
        return list(self.entries.values())[offset : offset + limit]

    def xǁInMemoryLedgerAdapterǁlist_entries__mutmut_2(self, limit: int = 100, offset: int = 1) -> list[LedgerEntry]:
        return list(self.entries.values())[offset : offset + limit]

    def xǁInMemoryLedgerAdapterǁlist_entries__mutmut_3(self, limit: int = 100, offset: int = 0) -> list[LedgerEntry]:
        return list(None)[offset : offset + limit]

    def xǁInMemoryLedgerAdapterǁlist_entries__mutmut_4(self, limit: int = 100, offset: int = 0) -> list[LedgerEntry]:
        return list(self.entries.values())[offset : offset - limit]

mutants_xǁInMemoryLedgerAdapterǁ__init____mutmut['_mutmut_orig'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁ__init____mutmut['xǁInMemoryLedgerAdapterǁ__init____mutmut_1'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁ__init____mutmut['xǁInMemoryLedgerAdapterǁ__init____mutmut_2'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁ__init____mutmut_2 # type: ignore # mutmut generated

mutants_xǁInMemoryLedgerAdapterǁis_processed__mutmut['_mutmut_orig'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁis_processed__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁis_processed__mutmut['xǁInMemoryLedgerAdapterǁis_processed__mutmut_1'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁis_processed__mutmut_1 # type: ignore # mutmut generated

mutants_xǁInMemoryLedgerAdapterǁmark_processed__mutmut['_mutmut_orig'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁmark_processed__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁmark_processed__mutmut['xǁInMemoryLedgerAdapterǁmark_processed__mutmut_1'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁmark_processed__mutmut_1 # type: ignore # mutmut generated

mutants_xǁInMemoryLedgerAdapterǁsave_entry__mutmut['_mutmut_orig'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁsave_entry__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁsave_entry__mutmut['xǁInMemoryLedgerAdapterǁsave_entry__mutmut_1'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁsave_entry__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁsave_entry__mutmut['xǁInMemoryLedgerAdapterǁsave_entry__mutmut_2'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁsave_entry__mutmut_2 # type: ignore # mutmut generated

mutants_xǁInMemoryLedgerAdapterǁget_entry__mutmut['_mutmut_orig'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁget_entry__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁget_entry__mutmut['xǁInMemoryLedgerAdapterǁget_entry__mutmut_1'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁget_entry__mutmut_1 # type: ignore # mutmut generated

mutants_xǁInMemoryLedgerAdapterǁlist_entries__mutmut['_mutmut_orig'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁlist_entries__mutmut_orig # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁlist_entries__mutmut['xǁInMemoryLedgerAdapterǁlist_entries__mutmut_1'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁlist_entries__mutmut_1 # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁlist_entries__mutmut['xǁInMemoryLedgerAdapterǁlist_entries__mutmut_2'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁlist_entries__mutmut_2 # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁlist_entries__mutmut['xǁInMemoryLedgerAdapterǁlist_entries__mutmut_3'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁlist_entries__mutmut_3 # type: ignore # mutmut generated
mutants_xǁInMemoryLedgerAdapterǁlist_entries__mutmut['xǁInMemoryLedgerAdapterǁlist_entries__mutmut_4'] = InMemoryLedgerAdapter.xǁInMemoryLedgerAdapterǁlist_entries__mutmut_4 # type: ignore # mutmut generated
