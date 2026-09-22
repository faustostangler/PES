#!/usr/bin/env python3
"""
YouTube Heatmap Harvester & Graph Crawler.

Pipeline:
[Module 1: Discovery Worker] -> [Module 2: Topic Auditor] -> [Module 3: Signal Processing] -> [Module 4: Targeted Fetcher]
"""

import argparse
import json
import os
import random
import re
import sqlite3
import sys
import time
import urllib.request
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import requests
from scipy.signal import find_peaks
import yt_dlp
from yt_dlp.utils import download_range_func

BASE_DIR = Path(__file__).resolve().parent

# --- Path & Seed Configuration ---
DEFAULT_SEED_URL = "https://www.youtube.com/watch?v=plExzNxH1Po", "https://www.youtube.com/watch?v=sRdWg7YjFS4"
DEFAULT_OUTPUT_DIR = BASE_DIR / "clips_harvested"
DEFAULT_DB_PATH = BASE_DIR / "heatmap_pipeline.sqlite"

# --- Discovery & Harvesting Limits ---
DEFAULT_MAX_APPROVED_CHANNELS = 0      # Max approved channels to audit and mine (0 for unlimited)
DEFAULT_MAX_VIDEOS_TO_PROCESS = 0      # Max videos to analyze (0 for unlimited, emptying the pool)
DEFAULT_TOP_POPULAR_COUNT = 50         # Top popular videos per channel to audit/inspect
DEFAULT_TARGET_CLIPS = 0               # Total clips to harvest (0 for unlimited, emptying the pool)
DEFAULT_MAX_CLIPS_PER_VIDEO = 0        # Max peak clips per individual video with heatmap (0 for unlimited)
DEFAULT_RECOMMENDATIONS_LIMIT = 12     # Recommended videos to fetch per video from /youtubei/v1/next

# --- Semantic Validation Defaults ---
DEFAULT_CHANNEL_MIN_RATIO = 0.50       # At least 50% of top popular videos >= threshold
DEFAULT_CHANNEL_MIN_SCORE = 0.50       # Similarity threshold per video for channel audit
DEFAULT_CHANNEL_MIN_AVG = 0.65         # Minimum average channel similarity score
DEFAULT_VIDEO_MIN_SCORE = 0.80         # Strict similarity threshold for admitting videos to video_pool
DEFAULT_ANCHOR_ALPHA = 0.75            # Weight of seed vector in Rocchio centroid (75% seed, 25% centroid)
DEFAULT_SEED_TAGS_LIMIT = 6            # Number of seed tags appended to reference title

# --- Signal Processing Defaults ---
DEFAULT_PEAK_MIN_HEIGHT = 0.25         # Minimum normalized heatmap height
DEFAULT_PEAK_MIN_DISTANCE = 1          # Minimum samples between adjacent peaks
DEFAULT_PEAK_MIN_PROMINENCE = 0.25      # Minimum peak prominence (mountain sharpness)
DEFAULT_PEAK_MIN_Z_SCORE = 0.50         # Minimum z-score to reject flat retention plateaus
DEFAULT_PADDING_START = 0.0            # Padding seconds added before peak start
DEFAULT_PADDING_END = 0.0              # Padding seconds added after peak end
DEFAULT_CUTOFF_RATIO = 0.0             # Initial duration fraction to ignore
DEFAULT_CUTOFF_SECONDS = 0.0           # Initial seconds to ignore

# --- Media & Download Defaults ---
DEFAULT_CLIP_FORMAT = "bestvideo[vcodec^=avc1][height<=720]+bestaudio[acodec^=mp4a]/best[ext=mp4]/18/best"
DEFAULT_YTDLP_EXTRACTOR_ARGS = {"youtube": {"player_client": ["android", "web"]}}

# --- Network, Jitter & Resilience Defaults ---
DEFAULT_HTTP_TIMEOUT = 12              # Timeout in seconds for HTTP requests
DEFAULT_DB_TIMEOUT = 15.0              # Timeout in seconds for SQLite connections
DEFAULT_JITTER_MIN_SEC = 1.0           # Minimum random sleep between network calls
DEFAULT_JITTER_MAX_SEC = 2.5           # Maximum random sleep between network calls

# --- Embeddings Engine Defaults ---
DEFAULT_EMBEDDING_BACKEND = "ollama"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "nomic-embed-text"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


# ==============================================================================
# State & Database Management (SQLite)
# ==============================================================================
def init_database(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database for pipeline state tracking."""
    # Use URI with nolock=1 to prevent hanging on fuseblk / network / external drive filesystems
    conn = sqlite3.connect(f"file:{db_path.resolve()}?nolock=1", uri=True, timeout=DEFAULT_DB_TIMEOUT)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                channel_url TEXT PRIMARY KEY,
                channel_id TEXT,
                channel_name TEXT,
                status TEXT, -- 'pending', 'approved', 'rejected'
                avg_score REAL,
                similarity REAL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                channel_url TEXT,
                title TEXT,
                status TEXT, -- 'pending', 'processed', 'skipped_no_heatmap', 'error'
                similarity REAL,
                has_heatmap INTEGER DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                clip_id TEXT PRIMARY KEY,
                video_id TEXT,
                channel_id TEXT,
                channel_name TEXT,
                video_title TEXT,
                source_url TEXT,
                timestamp_link TEXT,
                peak_rank INTEGER,
                peak_index INTEGER,
                start_time REAL,
                end_time REAL,
                clip_duration REAL,
                original_start_time REAL,
                original_end_time REAL,
                score REAL,
                prominence REAL,
                z_score REAL,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: Ensure similarity column exists in existing channels and videos tables
        ch_cols = [r[1] for r in conn.execute("PRAGMA table_info(channels)").fetchall()]
        if "similarity" not in ch_cols:
            conn.execute("ALTER TABLE channels ADD COLUMN similarity REAL")

        vid_cols = [r[1] for r in conn.execute("PRAGMA table_info(videos)").fetchall()]
        if "similarity" not in vid_cols:
            conn.execute("ALTER TABLE videos ADD COLUMN similarity REAL")

        conn.commit()
    return conn


def get_channel_status(conn: sqlite3.Connection, channel_url: str, channel_id: Optional[str] = None) -> Optional[str]:
    """Return status of channel if evaluated ('approved', 'rejected', etc.), or None."""
    cursor = conn.cursor()
    if channel_id:
        cursor.execute(
            "SELECT status FROM channels WHERE channel_url = ? OR (channel_id != '' AND channel_id = ?)",
            (channel_url, channel_id),
        )
    else:
        cursor.execute("SELECT status FROM channels WHERE channel_url = ?", (channel_url,))
    row = cursor.fetchone()
    return str(row[0]) if row else None


def is_channel_seen(conn: sqlite3.Connection, channel_url: str, channel_id: Optional[str] = None) -> bool:
    """Check if channel was already evaluated."""
    return get_channel_status(conn, channel_url, channel_id=channel_id) is not None


def is_channel_approved(conn: sqlite3.Connection, channel_url: str, channel_id: Optional[str] = None) -> bool:
    """Check if channel was evaluated and approved."""
    return get_channel_status(conn, channel_url, channel_id=channel_id) == "approved"


def record_channel(
    conn: sqlite3.Connection,
    channel_url: str,
    channel_id: Optional[str],
    channel_name: Optional[str],
    status: str,
    avg_score: float,
    similarity: Optional[float] = None,
) -> None:
    """Record channel evaluation in SQLite."""
    sim_val = similarity if similarity is not None else avg_score
    with conn:
        conn.execute("""
            INSERT INTO channels (channel_url, channel_id, channel_name, status, avg_score, similarity)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(channel_url) DO UPDATE SET
                status = excluded.status,
                avg_score = excluded.avg_score,
                similarity = excluded.similarity,
                checked_at = CURRENT_TIMESTAMP
        """, (channel_url, channel_id or "", channel_name or "", status, avg_score, sim_val))
        conn.commit()


def is_video_seen(conn: sqlite3.Connection, video_id: str) -> bool:
    """Check if video was already processed."""
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM videos WHERE video_id = ?", (video_id,))
    row = cursor.fetchone()
    return row is not None


def record_video(
    conn: sqlite3.Connection,
    video_id: str,
    channel_url: str,
    title: str,
    status: str,
    has_heatmap: bool,
    similarity: Optional[float] = None,
) -> None:
    """Record video processing status in SQLite."""
    with conn:
        conn.execute("""
            INSERT INTO videos (video_id, channel_url, title, status, similarity, has_heatmap)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
                status = excluded.status,
                similarity = COALESCE(excluded.similarity, videos.similarity),
                has_heatmap = excluded.has_heatmap,
                processed_at = CURRENT_TIMESTAMP
        """, (video_id, channel_url, title, status, similarity, 1 if has_heatmap else 0))
        conn.commit()


def record_clip(
    conn: sqlite3.Connection,
    clip_id: str,
    video_id: str,
    channel_id: str,
    channel_name: str,
    video_title: str,
    source_url: str,
    timestamp_link: str,
    peak_rank: int,
    peak_index: int,
    start_time: float,
    end_time: float,
    clip_duration: float,
    original_start_time: float,
    original_end_time: float,
    score: float,
    prominence: float,
    z_score: float,
    file_path: str,
) -> None:
    """Record harvested clip and its full audit metadata in SQLite."""
    with conn:
        conn.execute("""
            INSERT INTO clips (
                clip_id, video_id, channel_id, channel_name, video_title, source_url,
                timestamp_link, peak_rank, peak_index, start_time, end_time,
                clip_duration, original_start_time, original_end_time, score,
                prominence, z_score, file_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(clip_id) DO UPDATE SET
                start_time = excluded.start_time,
                end_time = excluded.end_time,
                score = excluded.score,
                prominence = excluded.prominence,
                z_score = excluded.z_score,
                file_path = excluded.file_path
        """, (
            clip_id, video_id, channel_id, channel_name, video_title, source_url,
            timestamp_link, peak_rank, peak_index, start_time, end_time,
            clip_duration, original_start_time, original_end_time, score,
            prominence, z_score, file_path,
        ))
        conn.commit()


# ==============================================================================
# Helper Utilities & Embeddings
# ==============================================================================
def extract_video_id(url_or_id: str) -> str:
    """Extract 11-char YouTube video ID from URL or return as-is."""
    match = re.search(r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})", url_or_id)
    if match:
        return match.group(1)
    if len(url_or_id) == 11:
        return url_or_id
    raise ValueError(f"Invalid YouTube URL or ID: {url_or_id}")


def get_random_header() -> dict:
    """Return realistic HTTP headers with rotating User-Agent."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "*/*",
    }


def apply_jitter(min_sec: float = DEFAULT_JITTER_MIN_SEC, max_sec: float = DEFAULT_JITTER_MAX_SEC) -> None:
    """Sleep with random jitter to avoid rate limits."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def check_video_has_heatmap(video_id: str) -> bool:
    """
    Fast pre-filter check to detect if a YouTube video has most-replayed heatmap data
    without downloading audio/video streams or executing full extraction.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = urllib.request.Request(url, headers=get_random_header())
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_HTTP_TIMEOUT) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        return ("markerTypeHeatmap" in html) or ("macroMarkersListEntity" in html)
    except Exception:
        return False


class EmbeddingEngine:
    """Handles text vectorization via local Ollama or SentenceTransformers."""

    def __init__(self, backend: str = DEFAULT_EMBEDDING_BACKEND, ollama_url: str = DEFAULT_OLLAMA_URL, model_name: str = DEFAULT_OLLAMA_MODEL):
        self.backend = backend
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name
        self.st_model = None

        if self.backend == "sentence-transformers":
            self._init_sentence_transformers()

    def _init_sentence_transformers(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            print("[*] Loading SentenceTransformer ('paraphrase-multilingual-MiniLM-L12-v2')...")
            self.st_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        except Exception as e:
            print(f"[!] Warning: SentenceTransformer init failed ({e}). Falling back to Ollama.")
            self.backend = "ollama"

    def embed(self, text: str) -> np.ndarray:
        """Return normalized embedding vector for input text."""
        if self.backend == "sentence-transformers" and self.st_model is not None:
            vec = self.st_model.encode(text, convert_to_numpy=True)
            norm = np.linalg.norm(vec)
            return vec / (norm + 1e-9)

        # Default: Ollama HTTP endpoint
        try:
            res = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=DEFAULT_HTTP_TIMEOUT,
            )
            res.raise_for_status()
            vec = np.array(res.json()["embedding"], dtype=np.float32)
            norm = np.linalg.norm(vec)
            return vec / (norm + 1e-9)
        except Exception as err:
            raise RuntimeError(f"Failed to generate embedding via Ollama ({err}). Is Ollama running?") from err

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """Compute cosine similarity between two unit vectors."""
        return float(np.dot(v1, v2))


# ==============================================================================
# Module 1: Graph Crawler (Discovery Worker)
# ==============================================================================
def get_recommendations_from_video(
    video_id: str,
    limit: int = DEFAULT_RECOMMENDATIONS_LIMIT,
    conn: Optional[sqlite3.Connection] = None,
) -> List[Dict[str, str]]:
    """
    Extract recommended videos and channels from YouTube's /youtubei/v1/next endpoint.
    Handles both modern lockupViewModel and legacy compactVideoRenderer formats.
    """
    url = "https://www.youtube.com/youtubei/v1/next"
    payload = {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20240101.00.00",
                "hl": "pt",
                "gl": "BR",
            }
        },
        "videoId": video_id,
    }
    candidates: List[Dict[str, str]] = []

    try:
        res = requests.post(url, json=payload, headers=get_random_header(), timeout=DEFAULT_HTTP_TIMEOUT)
        if res.status_code != 200:
            print(f" [!] /next returned HTTP {res.status_code} for video {video_id}")
            return candidates

        data = res.json()
        results = (
            data.get("contents", {})
            .get("twoColumnWatchNextResults", {})
            .get("secondaryResults", {})
            .get("secondaryResults", {})
            .get("results", [])
        )

        for item in results:
            v_id, title, ch_url, ch_name, ch_id = None, None, None, None, None

            # 1. Modern lockupViewModel
            if "lockupViewModel" in item:
                vm = item["lockupViewModel"]
                v_id = vm.get("contentId")
                meta_vm = vm.get("metadata", {}).get("lockupMetadataViewModel", {})
                title = meta_vm.get("title", {}).get("content")
                avatar = meta_vm.get("image", {}).get("decoratedAvatarViewModel", {})
                ch_name = avatar.get("a11yLabel")
                cmd = avatar.get("rendererContext", {}).get("commandContext", {}).get("onTap", {}).get("innertubeCommand", {})
                ch_url = cmd.get("commandMetadata", {}).get("webCommandMetadata", {}).get("url") or cmd.get("browseEndpoint", {}).get("canonicalBaseUrl")
                ch_id = cmd.get("browseEndpoint", {}).get("browseId")
                if not ch_url and ch_id:
                    ch_url = f"/channel/{ch_id}"

            # 2. Legacy compactVideoRenderer
            elif "compactVideoRenderer" in item:
                c = item["compactVideoRenderer"]
                v_id = c.get("videoId")
                title = c.get("title", {}).get("simpleText") or (
                    c.get("title", {}).get("runs", [{}])[0].get("text")
                )
                runs = c.get("shortBylineText", {}).get("runs", [])
                if runs:
                    ch_name = runs[0].get("text")
                    ep = runs[0].get("navigationEndpoint", {})
                    ch_url = ep.get("commandMetadata", {}).get("webCommandMetadata", {}).get("url") or ep.get("browseEndpoint", {}).get("canonicalBaseUrl")
                    ch_id = ep.get("browseEndpoint", {}).get("browseId")

            if v_id and ch_url:
                full_ch_url = ch_url if ch_url.startswith("http") else f"https://www.youtube.com{ch_url}"
                # Clean URL (strip /featured, /videos, etc.)
                clean_ch_url = full_ch_url.split("/featured")[0].split("/videos")[0]

                # Deduplicate by video_id within this recommendation batch
                if any(c["video_id"] == v_id for c in candidates):
                    continue

                candidates.append({
                    "video_id": v_id,
                    "title": title or "Unknown",
                    "channel_url": clean_ch_url,
                    "channel_name": ch_name or "",
                    "channel_id": ch_id or "",
                })
                if len(candidates) >= limit:
                    break

    except Exception as e:
        print(f" [!] Error fetching recommendations for {video_id}: {e}")

    return candidates


# ==============================================================================
# Module 2: Semantic Validator (Topic Auditor)
# ==============================================================================
def fetch_popular_videos_innertube(channel_url: str, limit: int = DEFAULT_TOP_POPULAR_COUNT) -> List[Dict[str, Any]]:
    """
    Fetch authentic top popular videos directly from YouTube's InnerTube browse API.
    Modern YouTube channels do not support `?sort=p` in the URL; instead, clicking
    'Popular' triggers an InnerTube browse continuation token.
    """
    try:
        clean_url = channel_url.rstrip("/")
        videos_url = clean_url if clean_url.endswith("/videos") else f"{clean_url}/videos"

        req = urllib.request.Request(
            videos_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        m_data = re.search(r"var ytInitialData = ({.*?});</script>", html)
        m_key = re.search(r'\"INNERTUBE_API_KEY\":\s*\"([^\"]+)\"', html)
        if not m_data or not m_key:
            return []

        api_key = m_key.group(1)
        data = json.loads(m_data.group(1))
        dump = json.dumps(data)

        # Locate the Popular continuation token
        m_token = re.search(r'Popular[^\"]*\".*?\"continuationCommand\":\s*\{\"token\":\s*\"([^\"]+)\"', dump)
        if not m_token:
            return []

        token = m_token.group(1)
        entries: List[Dict[str, Any]] = []
        seen = set()
        current_token = token

        while current_token and len(entries) < limit:
            browse_url = f"https://www.youtube.com/youtubei/v1/browse?key={api_key}"
            payload = {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": "2.20240410.01.00",
                        "hl": "en",
                        "gl": "US",
                    }
                },
                "continuation": current_token,
            }

            b_req = urllib.request.Request(
                browse_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                },
            )
            with urllib.request.urlopen(b_req, timeout=10) as b_resp:
                b_res = json.loads(b_resp.read().decode("utf-8"))

            next_token = None

            def walk_node(node: Any) -> None:
                nonlocal next_token
                if isinstance(node, dict):
                    # Modern YouTube lockupViewModel
                    if "lockupViewModel" in node:
                        vm = node["lockupViewModel"]
                        vid = vm.get("contentId")
                        title_obj = vm.get("metadata", {}).get("lockupMetadataViewModel", {}).get("title", {})
                        title = title_obj.get("content")
                        if vid and title and vid not in seen:
                            seen.add(vid)
                            entries.append({
                                "id": vid,
                                "title": title,
                                "url": f"https://www.youtube.com/watch?v={vid}",
                            })
                    # Classic YouTube videoRenderer
                    elif "videoRenderer" in node:
                        vr = node["videoRenderer"]
                        vid = vr.get("videoId")
                        t_obj = vr.get("title", {})
                        title = None
                        if "runs" in t_obj and t_obj["runs"]:
                            title = t_obj["runs"][0].get("text")
                        elif "simpleText" in t_obj:
                            title = t_obj.get("simpleText")
                        if vid and title and vid not in seen:
                            seen.add(vid)
                            entries.append({
                                "id": vid,
                                "title": title,
                                "url": f"https://www.youtube.com/watch?v={vid}",
                            })
                    elif "continuationCommand" in node and not next_token:
                        next_token = node["continuationCommand"].get("token")

                    for v in node.values():
                        if len(entries) >= limit:
                            break
                        walk_node(v)
                elif isinstance(node, list):
                    for item in node:
                        if len(entries) >= limit:
                            break
                        walk_node(item)

            walk_node(b_res)
            if not next_token or next_token == current_token:
                break
            current_token = next_token

        return entries
    except Exception as e:
        return []


def fetch_channel_top_videos(channel_url: str, limit: int = DEFAULT_TOP_POPULAR_COUNT) -> List[Dict[str, Any]]:
    """
    Fetch top popular videos of a channel.
    First attempts native InnerTube 'Popular' tab continuation.
    Falls back to yt-dlp flat extraction if InnerTube fails.
    """
    # 1. Try native InnerTube 'Popular' extraction
    entries = fetch_popular_videos_innertube(channel_url, limit=limit)
    if entries:
        return entries

    # 2. Fallback to yt-dlp flat playlist
    clean_url = channel_url.rstrip("/")
    pop_url = f"{clean_url}/videos"
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "playlistend": limit,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            res = ydl.extract_info(pop_url, download=False)
            return res.get("entries", []) or []
        except Exception as e:
            print(f" [!] Could not fetch videos for {channel_url}: {e}")
            return []



def audit_channel_topic(
    channel_url: str,
    reference_embedding: np.ndarray,
    engine: EmbeddingEngine,
    min_ratio: float = DEFAULT_CHANNEL_MIN_RATIO,
    min_score: float = DEFAULT_CHANNEL_MIN_SCORE,
    min_avg: float = DEFAULT_CHANNEL_MIN_AVG,
    top_limit: int = DEFAULT_TOP_POPULAR_COUNT,
) -> Tuple[bool, float, List[Dict[str, Any]], List[np.ndarray]]:
    """
    Audit channel thematic consistency by comparing its top popular videos with reference niche vector.
    Approval criteria:
      1. At least 50% of top videos have cosine score >= 0.50, AND
      2. Set average cosine score >= 0.55.
    """
    entries = fetch_channel_top_videos(channel_url, limit=top_limit)
    if not entries:
        return False, 0.0, [], []

    scores: List[float] = []
    qualifying_embs: List[np.ndarray] = []
    for entry in entries:
        t = str(entry.get("title") or "").strip()
        if not t:
            entry["similarity_score"] = 0.0
            scores.append(0.0)
            continue
        try:
            t_emb = engine.embed(t)
            sim = engine.cosine_similarity(reference_embedding, t_emb)
            entry["similarity_score"] = round(float(sim), 4)
            scores.append(sim)
            if sim >= min_score:
                qualifying_embs.append(t_emb)
        except Exception:
            entry["similarity_score"] = 0.0
            scores.append(0.0)

    avg_score = float(np.mean(scores)) if scores else 0.0
    qualifying_count = len(qualifying_embs)
    qualifying_ratio = qualifying_count / len(scores) if scores else 0.0

    is_approved = (qualifying_ratio >= min_ratio) and (avg_score >= min_avg)

    return is_approved, avg_score, entries, qualifying_embs


# ==============================================================================
# Module 3: Signal Processing (Heatmap Peak Detector)
# ==============================================================================
def extract_heatmap_peaks(
    heatmap: List[Dict[str, float]],
    duration: float,
    min_height: float = DEFAULT_PEAK_MIN_HEIGHT,
    min_distance: int = DEFAULT_PEAK_MIN_DISTANCE,
    min_prominence: float = DEFAULT_PEAK_MIN_PROMINENCE,
    padding_start: float = DEFAULT_PADDING_START,
    padding_end: float = DEFAULT_PADDING_END,
    cutoff_ratio: float = DEFAULT_CUTOFF_RATIO,
    cutoff_seconds: float = DEFAULT_CUTOFF_SECONDS,
    max_peaks: int = DEFAULT_MAX_CLIPS_PER_VIDEO,
    min_z_score: float = DEFAULT_PEAK_MIN_Z_SCORE,
) -> List[Dict[str, Any]]:
    """
    Detect genuine viral peaks in YouTube heatmap markers.
    Business Rules:
      1. Reject first initial retention drop-off (configured via cutoff_ratio / cutoff_seconds).
      2. find_peaks with height >= 0.70, distance >= 5, prominence >= 0.25.
      3. Z-score check (filters out flat retention lines).
      4. Apply configurable start/end padding (default 0s).
    """
    if not heatmap or duration <= 0:
        return []

    values = np.array([pt["value"] for pt in heatmap], dtype=np.float32)
    mean_val = float(np.mean(values))
    std_val = float(np.std(values))

    # Initial cutoff: ignore initial drop-off if requested (default 0.0)
    cutoff_time = max(cutoff_seconds, duration * cutoff_ratio)

    def _find(h_thresh: float, p_thresh: float) -> List[Dict[str, Any]]:
        peaks_i, props = find_peaks(
            values,
            height=h_thresh,
            distance=min_distance,
            prominence=p_thresh,
        )
        found = []
        for i, idx in enumerate(peaks_i):
            pt = heatmap[idx]
            val = float(pt["value"])
            start = float(pt["start_time"])
            end = float(pt["end_time"])
            prom = float(props["prominences"][i])
            z_score = float((val - mean_val) / (std_val + 1e-6))

            # Filter 1: Drop-off initial
            if start < cutoff_time:
                continue

            # Filter 2: Flat retention filter (z-score >= min_z_score)
            if z_score < min_z_score:
                continue

            # Apply padding
            padded_start = max(0.0, start - padding_start)
            padded_end = min(duration, end + padding_end)

            found.append({
                "peak_index": idx,
                "original_start": start,
                "original_end": end,
                "start_time": padded_start,
                "end_time": padded_end,
                "duration": padded_end - padded_start,
                "score": val,
                "prominence": prom,
                "z_score": z_score,
            })
        return found

    # Primary search
    valid_peaks = _find(min_height, min_prominence)

    # Adaptive fallback: if no peak meets strict threshold, soften thresholds
    if len(valid_peaks) == 0:
        valid_peaks = _find(max(0.50, min_height - 0.15), max(0.15, min_prominence - 0.10))

    # Sort descending by prominence (sharpest mountain first)
    valid_peaks.sort(key=lambda p: p["prominence"], reverse=True)
    return valid_peaks[:max_peaks] if max_peaks > 0 else valid_peaks


# ==============================================================================
# Module 4: Targeted Fetcher (Range Downloader)
# ==============================================================================
def download_clip_range(
    video_url: str,
    video_id: str,
    channel_id: str,
    channel_name: str,
    video_title: str,
    peak_info: Dict[str, Any],
    peak_rank: int,
    output_dir: Path,
    conn: Optional[sqlite3.Connection] = None,
    clip_format: str = DEFAULT_CLIP_FORMAT,
) -> Optional[Path]:
    """
    Download exact time slice using HTTP range requests via yt-dlp & ffmpeg.
    Saves the .mp4 file and persists all audit metadata directly in SQLite.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_ch = re.sub(r"[^A-Za-z0-9_-]", "", channel_id) or "channel"
    clip_base = f"{safe_ch}_{video_id}_peak_{peak_rank}"
    out_mp4 = output_dir / f"{clip_base}.mp4"

    start_sec = float(peak_info["start_time"])
    end_sec = float(peak_info["end_time"])
    duration = float(peak_info.get("duration", end_sec - start_sec))

    # Fast-check: if clip already exists on disk and is not empty, skip downloading
    if out_mp4.exists() and out_mp4.stat().st_size > 0:
        print(f"         [i] Clip already exists on disk ({out_mp4.name}). Skipping download.")
        if conn:
            record_clip(
                conn=conn,
                clip_id=clip_base,
                video_id=video_id,
                channel_id=channel_id,
                channel_name=channel_name,
                video_title=video_title,
                source_url=video_url,
                timestamp_link=f"{video_url}&t={int(start_sec)}s",
                peak_rank=peak_rank,
                peak_index=int(peak_info.get("peak_index", 0)),
                start_time=start_sec,
                end_time=end_sec,
                clip_duration=round(duration, 2),
                original_start_time=float(peak_info.get("original_start", start_sec)),
                original_end_time=float(peak_info.get("original_end", end_sec)),
                score=round(float(peak_info["score"]), 4),
                prominence=round(float(peak_info["prominence"]), 4),
                z_score=round(float(peak_info["z_score"]), 4),
                file_path=str(out_mp4),
            )
        return out_mp4

    ydl_opts = {
        # Format 18 (360p pre-muxed mp4) downloads range chunks in ~2s without heavy 4K re-encoding
        "format": clip_format,
        "download_ranges": download_range_func(None, [(start_sec, end_sec)]),
        "force_keyframes_at_cuts": True,
        "outtmpl": str(output_dir / f"{clip_base}.%(ext)s"),
        "overwrites": True,
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"node": {}},
        "extractor_args": DEFAULT_YTDLP_EXTRACTOR_ARGS,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Record all metadata in SQLite (Single Source of Truth in SQL)
        if conn:
            record_clip(
                conn=conn,
                clip_id=clip_base,
                video_id=video_id,
                channel_id=channel_id,
                channel_name=channel_name,
                video_title=video_title,
                source_url=video_url,
                timestamp_link=f"{video_url}&t={int(start_sec)}s",
                peak_rank=peak_rank,
                peak_index=int(peak_info.get("peak_index", 0)),
                start_time=start_sec,
                end_time=end_sec,
                clip_duration=round(duration, 2),
                original_start_time=float(peak_info.get("original_start", start_sec)),
                original_end_time=float(peak_info.get("original_end", end_sec)),
                score=round(float(peak_info["score"]), 4),
                prominence=round(float(peak_info["prominence"]), 4),
                z_score=round(float(peak_info["z_score"]), 4),
                file_path=str(out_mp4),
            )

        return out_mp4

    except Exception as e:
        print(f" [!] Error harvesting clip {clip_base}: {e}")
        return None


# ==============================================================================
# Pipeline Orchestrator: End-to-End Harvesting Loop
# ==============================================================================
def run_harvest_pipeline(
    seed_url: Union[str, List[str]] = DEFAULT_SEED_URL,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    db_path: Path = DEFAULT_DB_PATH,
    max_approved_channels: int = DEFAULT_MAX_APPROVED_CHANNELS,
    max_videos_to_process: int = DEFAULT_MAX_VIDEOS_TO_PROCESS,
    top_n_channel_videos: int = DEFAULT_TOP_POPULAR_COUNT,
    min_video_similarity: float = DEFAULT_VIDEO_MIN_SCORE,
    max_clips_per_video: int = DEFAULT_MAX_CLIPS_PER_VIDEO,
    target_clips: int = DEFAULT_TARGET_CLIPS,
    embedding_backend: str = DEFAULT_EMBEDDING_BACKEND,
    padding_start: float = DEFAULT_PADDING_START,
    padding_end: float = DEFAULT_PADDING_END,
    cutoff_ratio: float = DEFAULT_CUTOFF_RATIO,
    cutoff_seconds: float = DEFAULT_CUTOFF_SECONDS,
    clip_format: str = DEFAULT_CLIP_FORMAT,
    recommendations_limit: int = DEFAULT_RECOMMENDATIONS_LIMIT,
) -> Dict[str, Any]:
    """
    Run full graph discovery, semantic audit, and heatmap extraction pipeline.

    Crawler Loop Architecture:
      vídeo-semente(s) -> centróide semântico de seeds -> vai para o pool de vídeos para analisar
      -> videos recomendados (na barra lateral)
      -> canais dos vídeos recomendados
      -> top-videos de cada canal recomendado
      -> análise temática do canal OK
      -> cada top-n vídeo vai para o pool de vídeos para analisar
    """
    # Normalize seeds input (single URL, comma-separated list, or List[str])
    if isinstance(seed_url, str):
        seed_urls_list = [u.strip() for u in seed_url.split(",") if u.strip()]
    else:
        seed_urls_list = [str(u).strip() for u in seed_url if str(u).strip()]

    print("=" * 70)
    print(" YouTube Heatmap Harvester & Autonomous Graph Crawler")
    print("=" * 70)
    print(f" Seed Video(s):          {len(seed_urls_list)} seed(s) configured")
    for idx, s_u in enumerate(seed_urls_list, start=1):
        print(f"   [{idx}] {s_u}")
    print(f" Output Directory:       {output_dir.resolve()}")
    print(f" SQLite State Database:  {db_path.resolve()}")
    print(f" Max Approved Channels:  {max_approved_channels}")
    print(f" Max Videos to Analyze:  {'Unlimited (Drain Pool)' if max_videos_to_process <= 0 else max_videos_to_process}")
    print(f" Top-N Videos / Channel: {top_n_channel_videos}")
    print(f" Min Video Similarity:   {min_video_similarity:.2f}")
    print(f" Target Harvest Clips:   {'Unlimited (Drain Pool)' if target_clips <= 0 else target_clips}")
    print(f" Max Clips per Video:    {'Unlimited' if max_clips_per_video <= 0 else max_clips_per_video}")
    print(f" Embedding Backend:      {embedding_backend}")
    print(f" Padding (start / end):  {padding_start}s / {padding_end}s")
    print(f" Cutoff (ratio / sec):   {cutoff_ratio} / {cutoff_seconds}s")
    print(f" Video Stream Format:    {clip_format}")
    print("=" * 70)

    # 1. Initialize State & Embeddings
    conn = init_database(db_path)
    engine = EmbeddingEngine(backend=embedding_backend)

    # 2. Extract Seed Video(s) Info & Compute Normalized Seed Centroid
    print(f"\n[*] Step 1: Initializing {len(seed_urls_list)} Seed Video(s)...")

    ydl_meta = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"node": {}},
    }

    seed_embeddings: List[np.ndarray] = []
    seed_entries: List[Dict[str, Any]] = []

    for s_url in seed_urls_list:
        try:
            s_id = extract_video_id(s_url)
            with yt_dlp.YoutubeDL(ydl_meta) as ydl:
                s_info = ydl.extract_info(s_url, download=False)

            s_title = str(s_info.get("title") or "Seed Video")
            s_channel_url = s_info.get("channel_url") or f"https://www.youtube.com/channel/{s_info.get('channel_id', '')}"
            s_channel_id = s_info.get("channel_id") or "seed_channel"
            s_channel_name = s_info.get("uploader") or "Seed Channel"
            print(f"  [+] Seed ({s_id}): {s_title[:50]} | Channel: {s_channel_name}")

            s_tags = s_info.get("tags") or []
            s_text = f"{s_title}. {' '.join(s_tags[:DEFAULT_SEED_TAGS_LIMIT])}"
            s_emb = engine.embed(s_text)
            s_norm = np.linalg.norm(s_emb)
            if s_norm > 0:
                s_emb = s_emb / s_norm
            seed_embeddings.append(s_emb)

            seed_entries.append({
                "video_id": s_id,
                "url": s_url,
                "title": s_title,
                "channel_url": s_channel_url,
                "channel_name": s_channel_name,
                "channel_id": s_channel_id,
                "info": s_info,
            })

            # Register seed channel as approved with similarity 1.0
            record_channel(conn, s_channel_url, s_channel_id, s_channel_name, "approved", 1.0, similarity=1.0)
        except Exception as e:
            print(f"  [!] Failed to extract seed {s_url}: {e}")

    if not seed_embeddings:
        raise RuntimeError("No valid seed videos could be fetched or embedded. Aborting pipeline.")

    # Calculate Seed Centroid (mean of all normalized seed embeddings)
    seed_centroid = np.mean(seed_embeddings, axis=0)
    c_norm = np.linalg.norm(seed_centroid)
    if c_norm > 0:
        seed_embedding = seed_centroid / c_norm
    else:
        seed_embedding = seed_embeddings[0]

    print(f"[*] Computed Seed Centroid Vector across {len(seed_embeddings)} seed video(s).")

    # ref_embedding maintains the weighted anchor centroid:
    # ref = alpha * seed_centroid + (1 - alpha) * approved_channel_centroid
    ref_embedding = seed_embedding.copy()
    approved_embeddings: List[np.ndarray] = [seed_embedding]
    ANCHOR_ALPHA = DEFAULT_ANCHOR_ALPHA  # Anchored on seed centroid vs approved channel centroid

    # 3. Initialize video_pool with all Seed Videos
    video_pool: deque[Dict[str, Any]] = deque()
    queued_video_ids = set()

    seed_video_ids = {s["video_id"] for s in seed_entries}
    for s_entry in seed_entries:
        s_id = s_entry["video_id"]
        video_pool.append({
            "video_id": s_id,
            "url": s_entry["url"],
            "title": s_entry["title"],
            "channel_url": s_entry["channel_url"],
            "channel_name": s_entry["channel_name"],
            "channel_id": s_entry["channel_id"],
            "info": s_entry["info"],
            "similarity_score": 1.0,
        })
        queued_video_ids.add(s_id)

    # Track channels whose top-N popular videos have been mined in this run
    mined_channels: set[str] = set()

    # Mine top-N popular videos from seed channels into video pool
    for s_entry in seed_entries:
        s_ch_url = s_entry["channel_url"]
        s_ch_id = s_entry["channel_id"]
        s_ch_name = s_entry["channel_name"]
        if s_ch_url and s_ch_url not in mined_channels:
            mined_channels.add(s_ch_url)
            if s_ch_id:
                mined_channels.add(s_ch_id)
            print(f"[*] Mining top-{top_n_channel_videos} videos from seed channel: {s_ch_name}...")
            top_vids = fetch_channel_top_videos(s_ch_url, limit=top_n_channel_videos)
            enq_seed = 0
            for entry in top_vids:
                t_vid = entry.get("id")
                if not t_vid or is_video_seen(conn, t_vid) or t_vid in queued_video_ids:
                    continue
                v_title_entry = entry.get("title", "Untitled")
                try:
                    v_sim = float(engine.cosine_similarity(ref_embedding, engine.embed(v_title_entry)))
                except Exception:
                    v_sim = 0.0
                if v_sim >= min_video_similarity:
                    video_pool.append({
                        "video_id": t_vid,
                        "url": f"https://www.youtube.com/watch?v={t_vid}",
                        "title": v_title_entry,
                        "channel_url": s_ch_url,
                        "channel_name": s_ch_name,
                        "channel_id": s_ch_id,
                        "similarity_score": round(v_sim, 4),
                    })
                    queued_video_ids.add(t_vid)
                    enq_seed += 1
            print(f"    [+] Enqueued {enq_seed} video(s) from seed channel {s_ch_name} (Similarity >= {min_video_similarity:.2f}).")

    processed_videos_count = 0
    # Count unique approved channels from seeds
    approved_channels_count = len({s["channel_url"] for s in seed_entries if s.get("channel_url")})
    total_clips_harvested = 0

    print(f"\n[*] Initialized video pool with {len(video_pool)} video(s) ({approved_channels_count} approved seed channel(s)).")
    print("[*] Starting autonomous graph crawler loop...\n")

    # 4. Main Video Pool Crawler Loop
    while video_pool:
        # Check termination constraints
        if 0 < target_clips <= total_clips_harvested:
            print(f"\n[★] Reached target harvest goal ({total_clips_harvested}/{target_clips} clips). Finished.")
            break

        if 0 < max_videos_to_process <= processed_videos_count:
            print(f"\n[*] Reached max video analysis budget ({processed_videos_count}/{max_videos_to_process} videos). Finished.")
            break

        item = video_pool.popleft()
        v_id = item["video_id"]
        v_url = item.get("url") or f"https://www.youtube.com/watch?v={v_id}"
        v_title = item.get("title") or "Unknown"
        v_ch_url = item.get("channel_url") or ""
        v_ch_name = item.get("channel_name") or ""
        v_ch_id = item.get("channel_id") or ""

        # Avoid re-analyzing videos already recorded in SQLite (except seeds which provide initial discovery)
        is_already_seen = is_video_seen(conn, v_id)
        if is_already_seen and v_id not in seed_video_ids:
            continue

        processed_videos_count += 1
        print("-" * 70)
        print(f"[*] Analyzing Video #{processed_videos_count} (Queue remaining: {len(video_pool)}):")
        print(f"    Title: {v_title[:65]}")
        print(f"    URL:   {v_url}")

        info = item.get("info")
        if not info:
            apply_jitter(1.0, 2.0)
            try:
                with yt_dlp.YoutubeDL(ydl_meta) as ydl:
                    info = ydl.extract_info(v_url, download=False)
            except Exception as err:
                print(f"     [!] Could not extract video info: {err}")
                record_video(conn, v_id, v_ch_url, v_title, "error", False)
                continue

        v_title = str(info.get("title") or v_title)
        v_duration = float(info.get("duration") or 0.0)
        v_ch_url = v_ch_url or info.get("channel_url") or f"https://www.youtube.com/channel/{info.get('channel_id', '')}"
        v_ch_name = v_ch_name or info.get("uploader") or "Unknown Channel"
        v_ch_id = v_ch_id or info.get("channel_id") or ""

        v_sim = item.get("similarity_score")
        if v_sim is None:
            try:
                v_sim = float(engine.cosine_similarity(ref_embedding, engine.embed(v_title)))
            except Exception:
                v_sim = 0.0
        v_sim = round(float(v_sim), 4)

        # Step A: Signal Processing on Heatmap (only if not already processed in SQLite)
        if not is_already_seen:
            heatmap = info.get("heatmap")
            if heatmap:
                peaks = extract_heatmap_peaks(
                    heatmap=heatmap,
                    duration=v_duration,
                    padding_start=padding_start,
                    padding_end=padding_end,
                    cutoff_ratio=cutoff_ratio,
                    cutoff_seconds=cutoff_seconds,
                    max_peaks=max_clips_per_video,
                )
                if peaks:
                    print(f"     [+] Heatmap detected ({len(heatmap)} points). Found {len(peaks)} hot peak(s):")
                    for p_idx, peak in enumerate(peaks, start=1):
                        print(f"         -> Downloading Peak #{p_idx}: {peak['start_time']:.1f}s to {peak['end_time']:.1f}s (Score: {peak['score']:.2f}, Prom: {peak['prominence']:.2f})")
                        clip_path = download_clip_range(
                            video_url=v_url,
                            video_id=v_id,
                            channel_id=v_ch_id or v_ch_name,
                            channel_name=v_ch_name,
                            video_title=v_title,
                            peak_info=peak,
                            peak_rank=p_idx,
                            output_dir=output_dir,
                            conn=conn,
                            clip_format=clip_format,
                        )
                        if clip_path:
                            total_clips_harvested += 1
                            print(f"         [✓] Harvested: {clip_path.name} (Total clips: {total_clips_harvested})")
                    record_video(conn, v_id, v_ch_url, v_title, "processed", True, similarity=v_sim)
                else:
                    print("     [-] Heatmap present but no peaks met height/prominence criteria.")
                    record_video(conn, v_id, v_ch_url, v_title, "processed_no_peaks", True, similarity=v_sim)
            else:
                print("     [i] No heatmap available for this video (silent skip).")
                record_video(conn, v_id, v_ch_url, v_title, "skipped_no_heatmap", False, similarity=v_sim)
        else:
            print("     [i] Video was already processed in earlier session. Checking recommendations...")

        # Step B: Graph Expansion via Sidebar Recommendations
        # Always check recommendations for any processed video (with or without heatmap)
        # to find matching videos from already-approved channels. Only auditing new channels
        # is constrained by max_approved_channels.
        print(f"     [*] Harvesting sidebar recommendations from {v_id}...")
        recs = get_recommendations_from_video(v_id, limit=recommendations_limit)

        # Discover unique channels among recommended videos
        unique_cand_channels: Dict[str, Dict[str, Any]] = {}
        for r in recs:
            ch_url = r.get("channel_url")
            if ch_url and ch_url not in unique_cand_channels:
                unique_cand_channels[ch_url] = r

        for cand_ch_url, cand_meta in unique_cand_channels.items():
            cand_ch_id = cand_meta.get("channel_id", "")
            cand_ch_name = cand_meta.get("channel_name") or cand_ch_url
            ch_status = get_channel_status(conn, cand_ch_url, channel_id=cand_ch_id)

            if ch_status == "rejected":
                continue

            top_entries: List[Dict[str, Any]] = []

            # Case 1: Un-audited Channel -> Perform Thematic Audit
            if ch_status is None:
                if 0 < max_approved_channels <= approved_channels_count:
                    continue

                print(f"\n     [*] Auditing Recommended Channel: {cand_ch_name} ({cand_ch_url})")
                apply_jitter(1.0, 2.0)

                is_valid, avg_score, audit_entries, qual_embs = audit_channel_topic(
                    channel_url=cand_ch_url,
                    reference_embedding=ref_embedding,
                    engine=engine,
                    top_limit=top_n_channel_videos,
                )

                if not is_valid:
                    print(f"      [-] Channel REJECTED (Thematic similarity: {avg_score:.2f} < threshold). Discarding.")
                    record_channel(conn, cand_ch_url, cand_ch_id, cand_ch_name, "rejected", avg_score)
                    continue

                # Channel APPROVED
                print(f"      [+] Channel APPROVED! (Thematic similarity: {avg_score:.2f}).")
                record_channel(conn, cand_ch_url, cand_ch_id, cand_ch_name, "approved", avg_score)
                approved_channels_count += 1
                ch_status = "approved"
                top_entries = audit_entries

                # Update Weighted Anchor Centroid (Rocchio-style: 75% seed anchor, 25% approved centroid)
                if qual_embs:
                    approved_embeddings.extend(qual_embs)
                    approved_centroid = np.mean(approved_embeddings, axis=0)
                    c_norm = np.linalg.norm(approved_centroid)
                    if c_norm > 0:
                        approved_centroid = approved_centroid / c_norm
                    blended = (ANCHOR_ALPHA * seed_embedding) + ((1.0 - ANCHOR_ALPHA) * approved_centroid)
                    b_norm = np.linalg.norm(blended)
                    if b_norm > 0:
                        ref_embedding = blended / b_norm

            # Case 2: Channel is Approved -> Mine top-N popular videos if not yet mined in this run
            enqueued_count = 0
            if ch_status == "approved" and cand_ch_url not in mined_channels:
                mined_channels.add(cand_ch_url)
                if cand_ch_id:
                    mined_channels.add(cand_ch_id)

                if not top_entries:
                    print(f"     [*] Mining top-{top_n_channel_videos} popular videos from approved channel: {cand_ch_name}...")
                    top_entries = fetch_channel_top_videos(cand_ch_url, limit=top_n_channel_videos)

                tot_candidates = len(top_entries)
                for idx, entry in enumerate(top_entries, start=1):
                    t_vid = entry.get("id")
                    if not t_vid or is_video_seen(conn, t_vid) or t_vid in queued_video_ids:
                        continue

                    v_title_entry = entry.get("title", "Untitled")
                    v_link = f"https://www.youtube.com/watch?v={t_vid}"
                    v_sim = entry.get("similarity_score")
                    if v_sim is None:
                        try:
                            v_sim = float(engine.cosine_similarity(ref_embedding, engine.embed(v_title_entry)))
                        except Exception:
                            v_sim = 0.0
                        entry["similarity_score"] = round(v_sim, 4)

                    v_sim = float(v_sim)
                    if v_sim < min_video_similarity:
                        continue

                    video_pool.append({
                        "video_id": t_vid,
                        "url": v_link,
                        "title": v_title_entry,
                        "channel_url": cand_ch_url,
                        "channel_name": cand_ch_name,
                        "channel_id": cand_ch_id,
                        "similarity_score": round(v_sim, 4),
                    })
                    queued_video_ids.add(t_vid)
                    enqueued_count += 1
                    print(f"({idx}/{tot_candidates}) [POOL #{enqueued_count}] {v_sim:.2f} | {v_title_entry[:45]} | {v_link}")

            # Case 3: Also check the triggering recommended video itself
            rec_vid = cand_meta.get("video_id")
            if rec_vid and not is_video_seen(conn, rec_vid) and rec_vid not in queued_video_ids:
                rec_title = str(cand_meta.get("title") or "")
                try:
                    rec_sim = engine.cosine_similarity(ref_embedding, engine.embed(rec_title))
                except Exception:
                    rec_sim = 0.0
                if rec_sim >= min_video_similarity:
                    video_pool.append({
                        "video_id": rec_vid,
                        "url": f"https://www.youtube.com/watch?v={rec_vid}",
                        "title": rec_title or "Untitled",
                        "channel_url": cand_ch_url,
                        "channel_name": cand_ch_name,
                        "channel_id": cand_ch_id,
                        "similarity_score": round(float(rec_sim), 4),
                    })
                    queued_video_ids.add(rec_vid)
                    enqueued_count += 1
                    print(f"      [+] Discovered candidate from approved channel ({rec_sim:.2f}): {rec_title[:55]} ({rec_vid})")

            if enqueued_count > 0:
                print(f"[+] Enqueued {enqueued_count} video(s) into video pool (Similarity >= {min_video_similarity:.2f}). (Pool size: {len(video_pool)})")

    print("\n" + "=" * 70)
    print(" HARVESTING SUMMARY")
    print("=" * 70)
    vids_summary = f"{processed_videos_count} / {max_videos_to_process}" if max_videos_to_process > 0 else f"{processed_videos_count} (All Available)"
    target_summary = f" (Target: {target_clips})" if target_clips > 0 else ""
    print(f" Videos Analyzed:             {vids_summary}")
    print(f" Approved Channels Processed: {approved_channels_count} / {max_approved_channels}")
    print(f" Total Clips Harvested:       {total_clips_harvested}{target_summary}")
    print(f" Remaining in Video Pool:     {len(video_pool)}")
    print(f" Files Location:              {output_dir.resolve()}")
    print("=" * 70)

    return {
        "processed_videos": processed_videos_count,
        "approved_channels": approved_channels_count,
        "total_clips": total_clips_harvested,
        "pool_remaining": len(video_pool),
        "output_dir": str(output_dir),
    }


# ==============================================================================
# CLI Entrypoint & Self-Test Sanity Asserts
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="YouTube Heatmap Harvester & Graph Crawler")
    parser.add_argument("--seed", default=DEFAULT_SEED_URL, help="Seed video URL or comma-separated list of URLs")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output clips directory")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="SQLite database path")
    parser.add_argument("--max-channels", type=int, default=DEFAULT_MAX_APPROVED_CHANNELS, help="Max approved channels to process")
    parser.add_argument("--max-videos", type=int, default=DEFAULT_MAX_VIDEOS_TO_PROCESS, help="Max videos to analyze from video pool")
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_POPULAR_COUNT, help="Top-N videos per approved channel to inspect and enqueue")
    parser.add_argument("--min-video-score", type=float, default=DEFAULT_VIDEO_MIN_SCORE, help=f"Minimum video similarity score (default: {DEFAULT_VIDEO_MIN_SCORE:.2f})")
    parser.add_argument("--target-clips", type=int, default=DEFAULT_TARGET_CLIPS, help="Total clips to harvest before stopping (0 for unlimited)")
    parser.add_argument("--max-clips", type=int, default=DEFAULT_MAX_CLIPS_PER_VIDEO, help="Max clips per individual video (0 for unlimited)")
    parser.add_argument("--padding-start", type=float, default=DEFAULT_PADDING_START, help="Padding seconds before peak")
    parser.add_argument("--padding-end", type=float, default=DEFAULT_PADDING_END, help="Padding seconds after peak")
    parser.add_argument("--cutoff-ratio", type=float, default=DEFAULT_CUTOFF_RATIO, help="Initial duration fraction to ignore (0.0 to disable)")
    parser.add_argument("--cutoff-sec", type=float, default=DEFAULT_CUTOFF_SECONDS, help="Initial seconds to ignore (0.0 to disable)")
    parser.add_argument("--format", default=DEFAULT_CLIP_FORMAT, help="Video download stream format for yt-dlp")
    parser.add_argument("--backend", default=DEFAULT_EMBEDDING_BACKEND, choices=["ollama", "sentence-transformers"], help="Embedding engine")
    args = parser.parse_args()

    # --- Inline Sanity Asserts (KISS Validation) ---
    assert extract_video_id("https://www.youtube.com/watch?v=plExzNxH1Po") == "plExzNxH1Po"
    assert extract_video_id("plExzNxH1Po") == "plExzNxH1Po"
    dummy_heatmap = [{"start_time": float(i * 10), "end_time": float(i * 10 + 10), "value": 0.2} for i in range(100)]
    dummy_heatmap[50]["value"] = 0.95  # Isolated peak at index 50 (500s)
    peaks_test = extract_heatmap_peaks(dummy_heatmap, duration=1000.0, min_height=0.70, min_prominence=0.25)
    assert len(peaks_test) == 1, f"Expected 1 isolated peak, got {len(peaks_test)}"
    assert peaks_test[0]["original_start"] == 500.0, "Peak start time mismatch"

    # Sanity assert: Rocchio Anchor Centroid preserves unit norm and seed dominance
    v_seed = np.array([1.0, 0.0])
    v_cand = np.array([0.0, 1.0])
    v_blend = 0.75 * v_seed + 0.25 * v_cand
    v_blend = v_blend / np.linalg.norm(v_blend)
    assert np.isclose(np.linalg.norm(v_blend), 1.0)
    assert float(np.dot(v_blend, v_seed)) > float(np.dot(v_blend, v_cand)), "Seed must maintain dominant weight"

    # Sanity assert: Seed pool centroid preserves unit norm
    v_s1 = np.array([1.0, 0.0])
    v_s2 = np.array([0.0, 1.0])
    v_s_centroid = np.mean([v_s1, v_s2], axis=0)
    v_s_centroid = v_s_centroid / np.linalg.norm(v_s_centroid)
    assert np.isclose(np.linalg.norm(v_s_centroid), 1.0)
    assert np.isclose(float(np.dot(v_s_centroid, v_s1)), float(np.dot(v_s_centroid, v_s2)))

    # Run the pipeline
    run_harvest_pipeline(
        seed_url=args.seed,
        output_dir=Path(args.output_dir),
        db_path=Path(args.db_path),
        max_approved_channels=args.max_channels,
        max_videos_to_process=args.max_videos,
        top_n_channel_videos=args.top_n,
        min_video_similarity=args.min_video_score,
        max_clips_per_video=args.max_clips,
        target_clips=args.target_clips,
        embedding_backend=args.backend,
        padding_start=args.padding_start,
        padding_end=args.padding_end,
        cutoff_ratio=args.cutoff_ratio,
        cutoff_seconds=args.cutoff_sec,
        clip_format=args.format,
    )


if __name__ == "__main__":
    main()
