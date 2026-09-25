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
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from urllib.parse import unquote, urlparse

import numpy as np
import requests
from scipy.signal import find_peaks, peak_widths
import yt_dlp
from yt_dlp.utils import download_range_func

BASE_DIR = Path(__file__).resolve().parent

# --- Path & Seed Configuration ---
DEFAULT_SEED_URL: List[str] = [
    "https://www.youtube.com/watch?v=plExzNxH1Po",  # Barra da Tijuca Beach
    "https://www.youtube.com/watch?v=sRdWg7YjFS4",  # Leblon and Ipanema Beach
    "https://www.youtube.com/watch?v=sRRODmeZjPc",  # Copacabana Beach
    "https://www.youtube.com/watch?v=uo5PfoVNUgE",  # Downtown Rio de Janeiro
    "https://www.youtube.com/watch?v=c82VBPdZUkQ",
    "https://www.youtube.com/watch?v=Ron7LYbiIrc",
    "https://www.youtube.com/watch?v=BWi_ZMvGHvY", 
    "https://www.youtube.com/watch?v=LUs7bJH88yw", 
    "https://www.youtube.com/watch?v=yyP1ybjcjQ0",
    "https://www.youtube.com/watch?v=8ee1kBZM3H8",
    "https://www.youtube.com/watch?v=tQIVi12Vkoc",
    "https://www.youtube.com/watch?v=pmsanEmo-lU",
    "https://www.youtube.com/watch?v=1ZqgijX6P7o",
    "https://www.youtube.com/watch?v=6gFm5SrdFg4",
    "https://www.youtube.com/watch?v=u_iBlOLUcEY",
    "https://www.youtube.com/watch?v=8bW9KQLNTow",
    "https://www.youtube.com/watch?v=YqJHoKPGFp0",
    "https://www.youtube.com/watch?v=sBMo2roZ5js",
]

DEFAULT_ANTI_SEED_URL: List[str] = [
    "https://www.youtube.com/watch?v=3EOLT0KOv-k",  # Copacabana Reveillon / Night crowd
    "https://www.youtube.com/watch?v=GnoftmWev6c",  # Copacabana Boardwalk at night
    "https://www.youtube.com/watch?v=FQKFrlkz7dk",  # Porto Alegre (cold city / non-coastal)
    "https://www.youtube.com/watch?v=-XHD-LAy6Fc",  # Windstorm & rain chaos
]
def resolve_storage_path(path_or_uri: Union[str, Path]) -> Path:
    """Resolve standard POSIX paths or smb:// URIs to accessible local/GVFS mount points."""
    raw = str(path_or_uri)
    if raw.startswith("smb://"):
        parsed = urlparse(raw)
        server = parsed.hostname or "files.local"
        parts = unquote(parsed.path).strip("/").split("/", 1)
        share = parts[0] if parts else "public"
        sub_path = parts[1] if len(parts) > 1 else ""

        gvfs_mount = Path(f"/run/user/{os.getuid()}/gvfs") / f"smb-share:server={server},share={share}"
        if gvfs_mount.exists():
            return gvfs_mount / sub_path
    return Path(path_or_uri)


def sanitize_folder_name(name: str, max_length: int = 150) -> str:
    """Sanitize channel name or video title for safe directory naming across Linux, SMB and Windows."""
    if not name:
        return "unnamed"
    cleaned = name.replace(":", " -")
    cleaned = re.sub(r'[/\\*?"<>|]', "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.strip(". ")
    return (cleaned[:max_length].rstrip(". ")) or "unnamed"


DEFAULT_OUTPUT_DIR = resolve_storage_path(
    "smb://files.local/public/Fausto%20Stangler/Documentos/Videos/yt-heatmap/clips_harvested"
)
DEFAULT_DB_PATH = BASE_DIR / "heatmap_pipeline.sqlite"


def resolve_temp_dir(custom_path: Optional[Union[str, Path]] = None) -> Path:
    """Resolve scratch temporary directory prioritizing custom parameter, environment variable, or /mnt/gamer_d."""
    if custom_path:
        p = Path(custom_path)
    elif "HEATMAP_TEMP_DIR" in os.environ and os.environ["HEATMAP_TEMP_DIR"].strip():
        p = Path(os.environ["HEATMAP_TEMP_DIR"].strip())
    elif Path("/mnt/gamer_d/tmp/yt-heatmap").exists() or Path("/mnt/gamer_d").exists():
        p = Path("/mnt/gamer_d/tmp/yt-heatmap")
    else:
        p = Path(tempfile.gettempdir()) / "yt-heatmap"
    p.mkdir(parents=True, exist_ok=True)
    return p


DEFAULT_TEMP_DIR = resolve_temp_dir()

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
DEFAULT_VIDEO_MIN_SCORE = 0.50         # Similarity threshold for admitting videos to video_pool (0.50 with anti-seeds)
DEFAULT_ANCHOR_ALPHA = 0.75            # Weight of seed vector in Rocchio centroid (75% seed, 25% centroid)
DEFAULT_SEED_TAGS_LIMIT = 6            # Number of seed tags appended to reference title
DEFAULT_ANTI_SEED_BETA = 0.20          # Rocchio negative repulsion factor: C* = norm(C+ - beta * C-)
DEFAULT_ANTI_SEED_MARGIN = -0.025      # Contrastive guardrail: reject candidate if (sim_pos - sim_anti) <= margin (-0.025 buffer)

# --- Signal Processing Defaults ---
DEFAULT_PEAK_MIN_HEIGHT = 0.25         # Minimum normalized heatmap height
DEFAULT_PEAK_MIN_DISTANCE = 1          # Minimum samples between adjacent peaks
DEFAULT_PEAK_MIN_PROMINENCE = 0.15      # Minimum peak prominence (mountain sharpness)
DEFAULT_PEAK_MIN_Z_SCORE = 0.50         # Minimum z-score to reject flat retention plateaus
DEFAULT_PADDING_START = 0.0            # Padding seconds added before peak start
DEFAULT_PADDING_END = 0.0              # Padding seconds added after peak end
DEFAULT_CUTOFF_RATIO = 0.0             # Initial duration fraction to ignore
DEFAULT_CUTOFF_SECONDS = 0.0           # Initial seconds to ignore
DEFAULT_PEAK_CONTIGUOUS_FLOOR = 0.75  # (legacy) kept for reference — no longer used
DEFAULT_PEAK_WIDTH_REL_HEIGHT = 0.5   # Prominence fraction at which hot-zone width is measured (FWHM = 0.5)

# --- Media & Download Defaults ---
# SOTA-KISS video format selection:
#   1. Best 4K/1440p MP4 if available (height > 1080)
#   2. Best 1080p AVC1 (H.264) + AAC (m4a) for fast ffmpeg cuts and universal compatibility
#   3. Fallback to any 1080p stream + best audio
#   4. Fallback to best available video + audio
DEFAULT_CLIP_FORMAT = (
    "bestvideo[height>1080][ext=mp4]+bestaudio[ext=m4a]"
    "/bestvideo[vcodec^=avc1][height<=1080]+bestaudio[acodec^=mp4a]"
    "/bestvideo[height<=1080]+bestaudio"
    "/bestvideo+bestaudio"
    "/best"
)

# --- Network, Jitter & Resilience Defaults ---
DEFAULT_HTTP_TIMEOUT = 12              # Timeout in seconds for HTTP requests
DEFAULT_EMBEDDING_HTTP_TIMEOUT = 60    # Timeout in seconds for embedding generation (allows cold-start model load)
DEFAULT_DB_TIMEOUT = 15.0              # Timeout in seconds for SQLite connections
DEFAULT_JITTER_MIN_SEC = 1.0           # Minimum random sleep between network calls
DEFAULT_JITTER_MAX_SEC = 2.5           # Maximum random sleep between network calls
DEFAULT_MAX_DOWNLOAD_RETRIES = 3       # Maximum attempts to harvest an intact clip

# --- Embeddings Engine Defaults ---
DEFAULT_EMBEDDING_BACKEND = "ollama"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "nomic-embed-text"

# --- Authentication Cookies ---
# Auto-resolved at startup: checks well-known paths then extracts from browser.
DEFAULT_COOKIES_FILE: Optional[Path] = None   # Override with --cookies-file
DEFAULT_BROWSER_COOKIES: str = "firefox"       # Browser to extract from if no cookies file found
DEFAULT_COOKIES_MAX_AGE_HOURS: int = 12        # Force re-extraction if file is older than this

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

# Auth cookie names that confirm an authenticated YouTube session
_YT_AUTH_COOKIE_NAMES: frozenset = frozenset({
    "SID", "SSID", "HSID", "SAPISID", "APISID", "LOGIN_INFO",
    "__Secure-1PSID", "__Secure-3PSID", "__Secure-1PAPISID", "__Secure-3PAPISID",
})


def _has_auth_cookies(cookie_file: Path) -> bool:
    """Return True if the Netscape cookie file contains at least one YouTube auth token."""
    if not cookie_file.exists() or cookie_file.stat().st_size < 50:
        return False
    try:
        content = cookie_file.read_text(encoding="utf-8", errors="ignore")
        return any(f"\t{tok}\t" in content or content.endswith(f"\t{tok}") for tok in _YT_AUTH_COOKIE_NAMES)
    except OSError:
        return False


def resolve_cookies(
    cookies_file: Optional[Path] = None,
    browser: str = DEFAULT_BROWSER_COOKIES,
    max_age_hours: int = DEFAULT_COOKIES_MAX_AGE_HOURS,
    verbose: bool = True,
) -> Optional[Path]:
    """Resolve a valid YouTube Netscape cookie file, auto-extracting from a browser if needed.

    Resolution strategy (mirrors cresmo's ensure_cookies_file):
      1. If cookies_file is given and valid/fresh, use it directly.
      2. If missing/stale, try to extract from preferred browser (require auth tokens).
      3. Fallback: scan all supported browsers for any YouTube cookies.
      4. Return None if all attempts fail — pipeline continues unauthenticated.
    """
    import http.cookiejar
    import re as _re

    _SUPPORTED = ("firefox", "chrome", "chromium", "brave", "edge", "opera", "vivaldi")
    _DOMAINS = ("youtube.com", "google.com", "ytimg.com")
    _NAME_RE = _re.compile(r"^[!-~]+$")
    _VAL_RE = _re.compile(r"^[ -~]+$")

    # Candidate paths to check when no explicit file is given
    _candidates = [
        cookies_file,
        BASE_DIR / "cookies.txt",
        BASE_DIR / ".yt_dlp_cookies.txt",
        Path.home() / ".config" / "yt-dlp" / "cookies.txt",
    ]
    active: Optional[Path] = None
    for c in _candidates:
        if c and c.exists() and c.stat().st_size > 50:
            active = c
            break

    should_refresh = True
    if active and _has_auth_cookies(active):
        if max_age_hours <= 0:
            should_refresh = False
        else:
            age_h = (time.time() - active.stat().st_mtime) / 3600
            if age_h <= max_age_hours:
                should_refresh = False

    if not should_refresh:
        if verbose:
            print(f"[cookies] Using existing cookie file: {active}")
        return active

    # Try to extract fresh cookies via yt-dlp's browser extractor
    try:
        import yt_dlp.cookies as _yt_cookies
    except ImportError:
        _yt_cookies = None  # type: ignore[assignment]

    out_path = active or (BASE_DIR / "cookies.txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _extract(brw: str, require_auth: bool) -> bool:
        if _yt_cookies is None:
            return False
        try:
            cj = _yt_cookies.extract_cookies_from_browser(brw)
        except Exception as exc:
            if verbose:
                print(f"[cookies] Could not read from '{brw}': {exc}")
            return False
        if not cj:
            return False
        mcj = http.cookiejar.MozillaCookieJar(str(out_path))
        has_auth, count = False, 0
        for c in cj:
            dom = (c.domain or "").lower()
            if not any(dom.endswith(d) for d in _DOMAINS):
                continue
            if not c.name or not c.value or len(c.value.strip()) == 0:
                continue
            if not _NAME_RE.match(c.name) or not _VAL_RE.match(c.value):
                continue
            if c.name in _YT_AUTH_COOKIE_NAMES:
                has_auth = True
            mcj.set_cookie(c)
            count += 1
        if count == 0 or (require_auth and not has_auth):
            return False
        mcj.save(ignore_discard=True, ignore_expires=True)
        if verbose:
            auth_tag = "[Authenticated]" if has_auth else "[Guest]"
            print(f"[cookies] Saved {count} cookies {auth_tag} from '{brw}' -> {out_path.name}")
        return True

    priority = [browser] if browser in _SUPPORTED else []
    for b in ("firefox", "chrome", "chromium", "brave", "edge"):
        if b not in priority:
            priority.append(b)

    # First pass: authenticated session required
    for brw in priority:
        if _extract(brw, require_auth=True):
            return out_path
    # Second pass: any valid cookies (guest/unauthenticated)
    for brw in priority:
        if _extract(brw, require_auth=False):
            return out_path

    if active and _has_auth_cookies(active):
        if verbose:
            print(f"[cookies] Browser extraction failed; falling back to existing authenticated cookies: {active}")
        return active

    if verbose:
        print("[cookies] Could not extract cookies from any browser. Continuing unauthenticated.")
    return out_path if out_path.exists() and out_path.stat().st_size > 50 else None


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
                global_rank_index REAL,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Schema migration: ensure global_rank_index column exists for existing databases
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(clips)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "global_rank_index" not in existing_cols:
            conn.execute("ALTER TABLE clips ADD COLUMN global_rank_index REAL")

        # Backfill any existing clips missing global_rank_index
        conn.execute("""
            UPDATE clips
            SET global_rank_index = ROUND(
                prominence * MAX(0.0, z_score) * COALESCE(
                    (SELECT similarity FROM videos WHERE videos.video_id = clips.video_id),
                    1.0
                ),
                4
            )
            WHERE global_rank_index IS NULL
        """)

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
    global_rank_index: Optional[float] = None,
) -> None:
    """Record harvested clip and its full audit metadata in SQLite."""
    with conn:
        conn.execute("""
            INSERT INTO clips (
                clip_id, video_id, channel_id, channel_name, video_title, source_url,
                timestamp_link, peak_rank, peak_index, start_time, end_time,
                clip_duration, original_start_time, original_end_time, score,
                prominence, z_score, global_rank_index, file_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(clip_id) DO UPDATE SET
                start_time = excluded.start_time,
                end_time = excluded.end_time,
                score = excluded.score,
                prominence = excluded.prominence,
                z_score = excluded.z_score,
                global_rank_index = excluded.global_rank_index,
                file_path = excluded.file_path
        """, (
            clip_id, video_id, channel_id, channel_name, video_title, source_url,
            timestamp_link, peak_rank, peak_index, start_time, end_time,
            clip_duration, original_start_time, original_end_time, score,
            prominence, z_score, global_rank_index, file_path,
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
        "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
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
                timeout=DEFAULT_EMBEDDING_HTTP_TIMEOUT,
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


def evaluate_video_similarity(
    title: str,
    reference_embedding: np.ndarray,
    engine: EmbeddingEngine,
    pos_embedding: Optional[np.ndarray] = None,
    anti_embedding: Optional[np.ndarray] = None,
    anti_matrix: Optional[np.ndarray] = None,
    min_score: float = DEFAULT_VIDEO_MIN_SCORE,
    anti_margin: float = DEFAULT_ANTI_SEED_MARGIN,
) -> Tuple[bool, float, float]:
    """
    Evaluate video candidate against positive reference and anti-seed anchors.

    Decoupled Architecture:
      1. Base similarity threshold: ref_sim >= min_score against Rocchio-repelled anchor C*.
      2. Contrastive Margin Guardrail: (pos_sim - anti_sim) > anti_margin contrasting
         candidate against the pure positive centroid C+ vs negative anchor C-.
         Decoupling C+ from C* eliminates the double-penalty effect.

    Returns:
      (is_admitted, ref_similarity, anti_similarity)
    """
    try:
        t_emb = engine.embed(title)
        ref_sim = float(engine.cosine_similarity(reference_embedding, t_emb))
    except Exception:
        return False, 0.0, 0.0

    anti_sim = 0.0
    if anti_matrix is not None and len(anti_matrix) > 0:
        try:
            # 1-NN Hard Negative Metric: compare against the nearest individual negative exemplar.
            # Avoid blending with multi-modal centroid, which smooths out negative features
            # and creates an artificial vector in positive territory.
            anti_sim = float(np.max(np.dot(anti_matrix, t_emb)))
        except Exception:
            anti_sim = 0.0
    elif anti_embedding is not None:
        try:
            anti_sim = float(engine.cosine_similarity(anti_embedding, t_emb))
        except Exception:
            anti_sim = 0.0

    if ref_sim < min_score:
        return False, ref_sim, anti_sim

    # Decoupled contrastive guardrail: contrast candidate against pure positive anchor C+
    contrast_pos = pos_embedding if pos_embedding is not None else reference_embedding
    pos_sim = float(engine.cosine_similarity(contrast_pos, t_emb)) if pos_embedding is not None else ref_sim

    if (anti_embedding is not None or anti_matrix is not None) and (pos_sim - anti_sim) <= anti_margin:
        return False, ref_sim, anti_sim

    return True, ref_sim, anti_sim


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
    max_retries = 3

    results: List[Dict[str, Any]] = []
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.post(url, json=payload, headers=get_random_header(), timeout=DEFAULT_HTTP_TIMEOUT)
            if res.status_code != 200:
                if attempt < max_retries:
                    time.sleep(1.5 * attempt)
                    continue
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
            break
        except Exception as e:
            if attempt < max_retries:
                time.sleep(1.5 * attempt)
                continue
            print(f" [!] Error fetching recommendations for {video_id}: {e}")
            return candidates

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

        req = urllib.request.Request(videos_url, headers=get_random_header())
        with urllib.request.urlopen(req, timeout=DEFAULT_HTTP_TIMEOUT) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        m_data = re.search(r"var ytInitialData = ({.*?});</script>", html)
        m_key = re.search(r'\"INNERTUBE_API_KEY\":\s*\"([^\"]+)\"', html)
        if not m_data or not m_key:
            return []

        api_key = m_key.group(1)
        data = json.loads(m_data.group(1))
        dump = json.dumps(data)

        # Locate the Popular continuation token (supports English and Portuguese UI)
        m_token = re.search(r'(?:Popular|Mais populares)[^\"]*\".*?\"continuationCommand\":\s*\{\"token\":\s*\"([^\"]+)\"', dump, re.IGNORECASE)
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
                    **get_random_header(),
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(b_req, timeout=DEFAULT_HTTP_TIMEOUT) as b_resp:
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
    with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
        try:
            res = ydl.extract_info(pop_url, download=False)
            raw_entries = res.get("entries") if res else None
            if not raw_entries:
                return []
            return [dict(e) for e in cast(Any, raw_entries)]
        except Exception as e:
            print(f" [!] Could not fetch videos for {channel_url}: {e}")
            return []



def audit_channel_topic(
    channel_url: str,
    reference_embedding: np.ndarray,
    engine: EmbeddingEngine,
    pos_embedding: Optional[np.ndarray] = None,
    anti_embedding: Optional[np.ndarray] = None,
    anti_matrix: Optional[np.ndarray] = None,
    min_ratio: float = DEFAULT_CHANNEL_MIN_RATIO,
    min_score: float = DEFAULT_CHANNEL_MIN_SCORE,
    min_avg: float = DEFAULT_CHANNEL_MIN_AVG,
    top_limit: int = DEFAULT_TOP_POPULAR_COUNT,
    anti_margin: float = DEFAULT_ANTI_SEED_MARGIN,
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
            is_valid, sim, anti_sim = evaluate_video_similarity(
                title=t,
                reference_embedding=reference_embedding,
                engine=engine,
                pos_embedding=pos_embedding,
                anti_embedding=anti_embedding,
                anti_matrix=anti_matrix,
                min_score=min_score,
                anti_margin=anti_margin,
            )
            entry["similarity_score"] = round(float(sim), 4)
            if anti_embedding is not None or anti_matrix is not None:
                entry["anti_similarity_score"] = round(float(anti_sim), 4)
            scores.append(sim)
            if is_valid:
                qualifying_embs.append(engine.embed(t))
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
    peak_width_rel_height: float = DEFAULT_PEAK_WIDTH_REL_HEIGHT,
) -> List[Dict[str, Any]]:
    """
    Detect genuine viral peaks in YouTube heatmap markers.

    Business Rules:
      1. Reject first initial retention drop-off (configured via cutoff_ratio / cutoff_seconds).
      2. find_peaks with height >= min_height, distance >= min_distance, prominence >= min_prominence.
      3. Z-score check (filters out flat retention lines).
      4. Measure hot-zone width via ``scipy.signal.peak_widths`` at ``peak_width_rel_height``
         (default 0.5 = FWHM).  The threshold is ``peak_val - rel_height * prominence``,
         making it shape-invariant:
           - Platykurtic (broad plateau): prominence is small → floor is close to the peak
             value → width covers the full plateau.
           - Leptokurtic (sharp spike): prominence is large → floor is lower → width
             captures only the narrow spike.
      5. Apply configurable start/end padding on top of the hot zone (default 0 s).
    """
    if not heatmap or duration <= 0:
        return []

    n = len(heatmap)
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
        if len(peaks_i) == 0:
            return []

        # Measure hot-zone width for all peaks at once using prominence-relative height.
        # peak_widths returns fractional array indices (left_ips, right_ips); convert to
        # seconds using the uniform bucket width (duration / n).
        bucket_sec = duration / n
        _, _, left_ips, right_ips = peak_widths(values, peaks_i, rel_height=peak_width_rel_height)

        found = []
        for i, idx in enumerate(peaks_i):
            pt = heatmap[idx]
            val = float(pt["value"])
            # Canonical single-bucket reference (stored for audit)
            original_start = float(pt["start_time"])
            original_end = float(pt["end_time"])
            prom = float(props["prominences"][i])
            z_score = float((val - mean_val) / (std_val + 1e-6))

            # Filter 1: Drop-off initial
            if original_start < cutoff_time:
                continue

            # Filter 2: Flat retention filter (z-score >= min_z_score)
            if z_score < min_z_score:
                continue

            # Hot-zone boundaries from prominence-relative width (shape-invariant)
            zone_start = float(left_ips[i]) * bucket_sec
            zone_end = float(right_ips[i]) * bucket_sec

            # Apply padding around the hot zone
            padded_start = max(0.0, zone_start - padding_start)
            padded_end = min(duration, zone_end + padding_end)

            # Compute initial baseline Global Rank Index
            gri = round(prom * max(0.0, z_score), 4)

            found.append({
                "peak_index": idx,
                "original_start": original_start,
                "original_end": original_end,
                "start_time": padded_start,
                "end_time": padded_end,
                "duration": padded_end - padded_start,
                "score": val,
                "prominence": prom,
                "z_score": z_score,
                "global_rank_index": gri,
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
def is_clip_intact(file_path: Path, max_desync_sec: float = 2.0) -> bool:
    """Validate that a downloaded media clip contains intact, complete video and audio streams.

    Detects truncated clips where YouTube CDN severed the connection prematurely (leaving audio
    duration intact while video is frozen/cut short).
    """
    if not file_path.exists() or file_path.stat().st_size < 1024:
        return False
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,duration",
            "-of",
            "json",
            str(file_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode != 0:
            return False
        data = json.loads(res.stdout)
        streams = data.get("streams", [])
        v_dur = next(
            (float(s["duration"]) for s in streams if s.get("codec_type") == "video" and "duration" in s),
            None,
        )
        a_dur = next(
            (float(s["duration"]) for s in streams if s.get("codec_type") == "audio" and "duration" in s),
            None,
        )
        if v_dur is None:
            return False
        # If both audio and video exist, ensure video is not truncated compared to audio
        if a_dur is not None and (a_dur - v_dur) > max_desync_sec:
            return False
        return True
    except Exception:
        return False


def has_audio_stream(video_path: Path) -> bool:
    """Check if the media file contains an audio stream."""
    try:
        res = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "a",
                "-show_entries", "stream=codec_type",
                "-of", "csv=p=0",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return "audio" in res.stdout
    except Exception:
        return True


def format_time(sec: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    s = max(0, int(sec))
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def run_ffmpeg_with_progress(
    cmd: List[str],
    expected_duration_sec: float = 0.0,
    label: str = "NVENC",
    timeout: int = 1800,
) -> Tuple[int, str]:
    """
    Execute ffmpeg command with real-time ETA, speed, and percentage progress bar.
    Reads progress events via '-progress pipe:1 -nostats'.
    """
    full_cmd = [cmd[0], "-y", "-progress", "pipe:1", "-nostats"] + [a for a in cmd[1:] if a != "-y"]

    t0 = time.time()
    stderr_lines: List[str] = []
    curr_sec = 0.0
    speed_val = 0.0
    fps_val = 0.0

    try:
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
    except Exception as e:
        return -1, str(e)

    def read_stderr():
        if proc.stderr:
            for line in proc.stderr:
                stderr_lines.append(line.strip())

    t_err = threading.Thread(target=read_stderr, daemon=True)
    t_err.start()

    try:
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                line = line.strip()
                if not line or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k == "out_time_us" and v.isdigit():
                    curr_sec = int(v) / 1_000_000.0
                elif k == "speed":
                    s_str = v.rstrip("x").strip()
                    try:
                        speed_val = float(s_str)
                    except ValueError:
                        pass
                elif k == "fps":
                    try:
                        fps_val = float(v)
                    except ValueError:
                        pass
                elif k == "progress" and v in ("continue", "end"):
                    pct = min(99.9, (curr_sec / expected_duration_sec) * 100.0) if expected_duration_sec > 0 else 0.0
                    rem_sec = max(0.0, expected_duration_sec - curr_sec)
                    eta_sec = (rem_sec / speed_val) if speed_val > 0 else 0.0
                    filled = int(pct / 5)
                    bar = "█" * filled + "░" * (20 - filled)
                    speed_display = f"{speed_val:.1f}x" if speed_val > 0 else "..."
                    fps_display = f" ({int(fps_val)} fps)" if fps_val > 0 else ""
                    dur_display = (
                        f"{format_time(curr_sec)}/{format_time(expected_duration_sec)}"
                        if expected_duration_sec > 0
                        else format_time(curr_sec)
                    )
                    eta_display = (
                        f" | ETA: {format_time(eta_sec)}"
                        if (expected_duration_sec > 0 and speed_val > 0)
                        else ""
                    )

                    sys.stdout.write(
                        f"\r         [{label}] [{bar}] {pct:5.1f}% | {dur_display} | {speed_display}{fps_display}{eta_display}   "
                    )
                    sys.stdout.flush()

        proc.wait(timeout=timeout)
        t_err.join(timeout=2.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        sys.stdout.write("\n")
        return -1, "Timed out"
    except Exception as e:
        proc.kill()
        sys.stdout.write("\n")
        return -1, str(e)

    elapsed = time.time() - t0
    avg_speed = (expected_duration_sec / elapsed) if (expected_duration_sec > 0 and elapsed > 0) else speed_val

    if proc.returncode == 0:
        bar = "█" * 20
        dur_display = format_time(expected_duration_sec) if expected_duration_sec > 0 else format_time(curr_sec)
        sys.stdout.write(
            f"\r         [{label}] [{bar}] 100.0% | {dur_display} finished in {elapsed:.1f}s ({avg_speed:.1f}x avg)       \n"
        )
        sys.stdout.flush()
    else:
        sys.stdout.write("\n")

    return proc.returncode, "\n".join(stderr_lines[-10:])


def safe_copy_file(src: Path, dst: Path, chunk_size: int = 16 * 1024 * 1024) -> None:
    """Stream file bytes in chunks with throughput progress to prevent [Errno 95] on GVFS/FUSE."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    total_bytes = src.stat().st_size
    copied = 0
    t0 = time.time()
    last_print = t0

    print(f"         [*] Transferring to storage: {dst.name} ({total_bytes / (1024 * 1024):.1f} MB)...")
    with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
        while True:
            chunk = fsrc.read(chunk_size)
            if not chunk:
                break
            fdst.write(chunk)
            copied += len(chunk)
            now = time.time()
            if now - last_print >= 1.0 or copied == total_bytes:
                elapsed = max(0.001, now - t0)
                speed_mb = (copied / (1024 * 1024)) / elapsed
                pct = (copied / total_bytes) * 100 if total_bytes > 0 else 100
                rem_bytes = max(0, total_bytes - copied)
                eta_sec = rem_bytes / (speed_mb * 1024 * 1024) if speed_mb > 0 else 0
                eta_str = f"{int(eta_sec // 60):02d}:{int(eta_sec % 60):02d}"
                bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
                sys.stdout.write(
                    f"\r         [Storage Copy] [{bar}] {pct:5.1f}% | {copied / (1024 * 1024):.1f}/{total_bytes / (1024 * 1024):.1f} MB | {speed_mb:.1f} MB/s | ETA: {eta_str}   "
                )
                sys.stdout.flush()
                last_print = now

    sys.stdout.write("\n")
    sys.stdout.flush()


def merge_and_slowdown_clips(
    clip_paths: List[Path],
    output_path: Path,
    speed_factor: float = 1.0,
    temp_dir: Optional[Path] = None,
    expected_duration: Optional[float] = None,
) -> bool:
    """
    Concatenate video clips at native 1x speed without re-encoding (stream copy).
    Uses fast bitstream remux (-c copy), falling back to re-encoding only if needed.
    """
    if not clip_paths:
        return False

    valid_clips = [c for c in clip_paths if c.exists() and c.stat().st_size > 0]
    if not valid_clips:
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    scratch = temp_dir or DEFAULT_TEMP_DIR
    scratch.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, dir=scratch) as f:
        for c in valid_clips:
            esc = str(c.resolve()).replace("'", "'\\''")
            f.write(f"file '{esc}'\n")
        concat_file = Path(f.name)

    # Encode to local scratch temp file first to avoid network latency and corruption on network/SMB shares
    local_temp = scratch / f"merged_{output_path.name}"
    if local_temp.exists():
        try:
            local_temp.unlink()
        except Exception:
            pass

    # Primary Method: Instant Stream Copy (-c copy) at native 1x speed
    cmd_copy = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy",
        str(local_temp),
    ]

    success = False
    t_remux = time.time()
    try:
        r = subprocess.run(cmd_copy, capture_output=True, text=True, timeout=600)
        if r.returncode == 0 and local_temp.exists() and local_temp.stat().st_size > 0 and is_clip_intact(local_temp):
            success = True
            print(f"         [✓] Fast remux finished in {time.time() - t_remux:.2f}s ({local_temp.stat().st_size / (1024 * 1024):.1f} MB)")
        else:
            # Fallback: NVENC Hardware Re-encode if stream copy fails
            has_audio = has_audio_stream(valid_clips[0])
            map_args = ["-map", "0:v", "-map", "0:a"] if has_audio else ["-map", "0:v"]
            cmd_nvenc = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_file),
                *map_args,
                "-c:v", "h264_nvenc", "-preset", "p1", "-cq", "21", "-pix_fmt", "yuv420p",
            ]
            if has_audio:
                cmd_nvenc.extend(["-c:a", "aac", "-b:a", "192k"])
            cmd_nvenc.append(str(local_temp))

            ret, err = run_ffmpeg_with_progress(
                cmd_nvenc,
                expected_duration_sec=expected_duration or 0.0,
                label="NVENC",
                timeout=1800,
            )
            if ret == 0 and local_temp.exists() and local_temp.stat().st_size > 0 and is_clip_intact(local_temp):
                success = True
            else:
                err_msg = err.strip().splitlines()[-1] if err.strip() else f"exit {ret}"
                print(f"         [!] NVENC failed ({err_msg}), falling back to CPU (libx264 veryfast)...")
                cmd_cpu = [
                    "ffmpeg", "-y",
                    "-f", "concat", "-safe", "0", "-i", str(concat_file),
                    *map_args,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                ]
                if has_audio:
                    cmd_cpu.extend(["-c:a", "aac", "-b:a", "192k"])
                cmd_cpu.append(str(local_temp))
                ret2, err2 = run_ffmpeg_with_progress(
                    cmd_cpu,
                    expected_duration_sec=expected_duration or 0.0,
                    label="CPU",
                    timeout=3600,
                )
                if ret2 == 0 and local_temp.exists() and local_temp.stat().st_size > 0:
                    success = True
                else:
                    print(f"         [!] CPU ffmpeg failed: {err2}")
    except Exception as e:
        print(f"         [!] Error merging clips: {e}")
    finally:
        concat_file.unlink(missing_ok=True)

    if success and local_temp.exists() and is_clip_intact(local_temp):
        try:
            safe_copy_file(local_temp, output_path)
            local_temp.unlink(missing_ok=True)
            return True
        except Exception as e:
            print(f"         [!] Error copying {local_temp} -> {output_path}: {e}")
            return False
    else:
        if local_temp.exists():
            local_temp.unlink(missing_ok=True)
        return False


def download_single_peak_temp(
    video_url: str,
    peak_info: Dict[str, Any],
    temp_dir: Path,
    peak_idx: int,
    clip_format: str = DEFAULT_CLIP_FORMAT,
    cookie_path: Optional[Union[str, Path]] = None,
    max_retries: int = DEFAULT_MAX_DOWNLOAD_RETRIES,
) -> Tuple[Optional[Path], Optional[int]]:
    """
    Download a single heatmap peak time slice into a temporary folder.
    Returns (clip_path, resolution_height).
    """
    start_sec = float(peak_info["start_time"])
    end_sec = float(peak_info["end_time"])
    prefix = f"peak_{peak_idx}"

    for attempt in range(1, max_retries + 1):
        _captured: Dict[str, Any] = {"height": None, "filename": None}

        def _capture_resolution(d: Dict[str, Any]) -> None:
            if d.get("status") == "finished":
                h = d.get("height") or d.get("info_dict", {}).get("height")
                if h:
                    _captured["height"] = int(h)
                fn = d.get("filename")
                if fn:
                    _captured["filename"] = Path(fn)

        ydl_opts: Dict[str, Any] = {
            "format": clip_format,
            "download_ranges": download_range_func([], cast(Any, [(start_sec, end_sec)])),
            "force_keyframes_at_cuts": False,
            "outtmpl": str(temp_dir / f"{prefix}.%(ext)s"),
            "overwrites": True,
            "quiet": True,
            "no_warnings": True,
            "js_runtimes": {"node": {}},
            "socket_timeout": 30,
            "retries": 10,
            "external_downloader_args": {
                "ffmpeg_i": ["-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5"]
            },
            "progress_hooks": [_capture_resolution],
        }
        if cookie_path and Path(cookie_path).exists():
            ydl_opts["cookiefile"] = str(cookie_path)

        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                ydl.download([video_url])

            downloaded = _captured.get("filename")
            if downloaded is None or not downloaded.exists():
                for ext in (".mp4", ".mkv", ".webm"):
                    cand = temp_dir / f"{prefix}{ext}"
                    if cand.exists():
                        downloaded = cand
                        break

            if downloaded and downloaded.exists() and is_clip_intact(downloaded):
                return downloaded, _captured.get("height")
            else:
                if downloaded and downloaded.exists():
                    downloaded.unlink(missing_ok=True)
                if attempt < max_retries:
                    time.sleep(random.uniform(1.5, 3.0) * attempt)
        except Exception:
            if attempt < max_retries:
                time.sleep(random.uniform(1.5, 3.0))

    return None, None


def harvest_video_merged(
    video_url: str,
    video_id: str,
    channel_id: str,
    channel_name: str,
    video_title: str,
    peaks: List[Dict[str, Any]],
    output_dir: Path,
    conn: Optional[sqlite3.Connection] = None,
    clip_format: str = DEFAULT_CLIP_FORMAT,
    cookies_file: Optional[Union[str, Path]] = None,
    video_similarity: Optional[float] = None,
    temp_dir: Optional[Path] = None,
) -> Optional[Path]:
    """
    Harvest all heatmap peaks for a video, download into temporary scratch space,
    concatenate in chronological order at 50% speed (2x duration), and save exclusively
    as a single merged video: channel_dir / f"{safe_video}_{resolution}p.mp4".
    No individual clips are left on disk.
    Persists clip audit metadata in SQLite with file_path pointing to the merged video.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_ch_id = re.sub(r"[^A-Za-z0-9_-]", "", channel_id) or "channel"
    safe_channel = sanitize_folder_name(channel_name or safe_ch_id)
    safe_video = sanitize_folder_name(video_title or video_id, max_length=160)
    channel_dir = output_dir / safe_channel
    channel_dir.mkdir(parents=True, exist_ok=True)

    # Check if merged video already exists on disk
    existing: Optional[Path] = next(channel_dir.glob(f"{safe_video}_*p.mp4"), None)
    if existing is None:
        cand = channel_dir / f"{safe_video}.mp4"
        if cand.exists():
            existing = cand

    if existing is not None and existing.stat().st_size > 0 and is_clip_intact(existing):
        print(f"         [i] Merged video already exists: {existing.name}")
        return existing

    cookie_path = cookies_file or resolve_cookies(verbose=False)
    sim = float(video_similarity if video_similarity is not None else 1.0)

    # Sort peaks chronologically for coherent narrative playback
    sorted_peaks = sorted(peaks, key=lambda p: float(p.get("start_time", 0.0)))

    scratch = temp_dir or DEFAULT_TEMP_DIR
    scratch.mkdir(parents=True, exist_ok=True)

    temp_dir_obj = tempfile.TemporaryDirectory(prefix=f"harvest_{video_id}_", dir=scratch)
    temp_dir_path = Path(temp_dir_obj.name)

    downloaded_clips: List[Tuple[Dict[str, Any], int, Path, Optional[int]]] = []
    max_height: Optional[int] = None

    try:
        for p_idx, peak in enumerate(sorted_peaks, start=1):
            gri = round(float(peak.get("prominence", 0.0)) * max(0.0, float(peak.get("z_score", 0.0))) * max(0.1, sim), 4)
            peak["global_rank_index"] = gri
            print(f"         -> Downloading Peak #{p_idx}/{len(sorted_peaks)}: {peak['start_time']:.1f}s to {peak['end_time']:.1f}s (Prom: {peak.get('prominence', 0):.2f}, GRI: {gri:.3f})")
            clip_path, h = download_single_peak_temp(
                video_url=video_url,
                peak_info=peak,
                temp_dir=temp_dir_path,
                peak_idx=p_idx,
                clip_format=clip_format,
                cookie_path=cookie_path,
            )
            if clip_path and is_clip_intact(clip_path):
                downloaded_clips.append((peak, p_idx, clip_path, h))
                if h and (max_height is None or h > max_height):
                    max_height = h
            else:
                print(f"         [!] Could not harvest peak #{p_idx}, skipping this segment...")

        if not downloaded_clips:
            print(f"         [!] No clips successfully harvested for {video_id}.")
            return None

        # Determine target merged filename
        res_suffix = f"_{max_height}p" if max_height else ""
        target_path = channel_dir / f"{safe_video}{res_suffix}.mp4"

        print(f"         [*] Compiling {len(downloaded_clips)} clips into merged video: {target_path.name} (1x stream copy)...")
        total_in_sec = sum(
            float(p.get("duration") or (float(p["end_time"]) - float(p["start_time"])))
            for p, _, _, _ in downloaded_clips
        )
        expected_output_sec = total_in_sec if total_in_sec > 0 else 0.0

        clip_paths_only = [item[2] for item in downloaded_clips]
        ok = merge_and_slowdown_clips(
            clip_paths_only,
            target_path,
            speed_factor=1.0,
            temp_dir=scratch,
            expected_duration=expected_output_sec,
        )
        if not ok or not target_path.exists() or not is_clip_intact(target_path):
            print(f"         [!] Failed to compile merged video for {video_id}.")
            return None

        # Persist all individual clip metadata in SQLite (Single Source of Truth) pointing to merged video
        if conn:
            for peak, rank, _, _ in downloaded_clips:
                clip_id = f"{safe_ch_id}_{video_id}_peak_{rank}"
                start_sec = float(peak["start_time"])
                end_sec = float(peak["end_time"])
                duration = float(peak.get("duration", end_sec - start_sec))
                record_clip(
                    conn=conn,
                    clip_id=clip_id,
                    video_id=video_id,
                    channel_id=channel_id,
                    channel_name=channel_name,
                    video_title=video_title,
                    source_url=video_url,
                    timestamp_link=f"{video_url}&t={int(start_sec)}s",
                    peak_rank=rank,
                    peak_index=int(peak.get("peak_index", 0)),
                    start_time=start_sec,
                    end_time=end_sec,
                    clip_duration=round(duration, 2),
                    original_start_time=float(peak.get("original_start", start_sec)),
                    original_end_time=float(peak.get("original_end", end_sec)),
                    score=round(float(peak["score"]), 4),
                    prominence=round(float(peak["prominence"]), 4),
                    z_score=round(float(peak["z_score"]), 4),
                    global_rank_index=float(peak.get("global_rank_index", 0.0)),
                    file_path=str(target_path),
                )

        return target_path
    finally:
        # Guarantee all temporary individual clips are cleaned up and never left on disk
        temp_dir_obj.cleanup()


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
    cookies_file: Optional[Union[str, Path]] = None,
    max_retries: int = DEFAULT_MAX_DOWNLOAD_RETRIES,
    video_similarity: Optional[float] = None,
    temp_dir: Optional[Path] = None,
) -> Optional[Path]:
    """Backward compatibility alias: delegates to harvest_video_merged for single clip."""
    return harvest_video_merged(
        video_url=video_url,
        video_id=video_id,
        channel_id=channel_id,
        channel_name=channel_name,
        video_title=video_title,
        peaks=[peak_info],
        output_dir=output_dir,
        conn=conn,
        clip_format=clip_format,
        cookies_file=cookies_file,
        video_similarity=video_similarity,
        temp_dir=temp_dir,
    )


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
    cookies_file: Optional[Path] = None,
    browser_cookies: str = DEFAULT_BROWSER_COOKIES,
    anti_seed_url: Optional[Union[str, List[str]]] = None,
    anti_beta: float = DEFAULT_ANTI_SEED_BETA,
    anti_margin: float = DEFAULT_ANTI_SEED_MARGIN,
    temp_dir: Path = DEFAULT_TEMP_DIR,
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
    output_dir = resolve_storage_path(output_dir)
    temp_dir = resolve_temp_dir(temp_dir)

    # Normalize seeds input (single URL, comma-separated list, or List[str])
    if isinstance(seed_url, str):
        seed_urls_list = [u.strip() for u in seed_url.split(",") if u.strip()]
    else:
        seed_urls_list = [u.strip() for u in seed_url if u.strip()]

    # Normalize anti-seeds input
    if anti_seed_url is None:
        anti_seed_urls_list = [u.strip() for u in DEFAULT_ANTI_SEED_URL if u.strip()]
    elif isinstance(anti_seed_url, str):
        anti_seed_urls_list = [u.strip() for u in anti_seed_url.split(",") if u.strip()]
    else:
        anti_seed_urls_list = [u.strip() for u in anti_seed_url if u.strip()]

    print("=" * 70)
    print(" YouTube Heatmap Harvester & Autonomous Graph Crawler")
    print("=" * 70)
    print(f" Seed Video(s):          {len(seed_urls_list)} seed(s) configured")
    for idx, s_u in enumerate(seed_urls_list, start=1):
        print(f"   [{idx}] {s_u}")
    if anti_seed_urls_list:
        print(f" Anti-Seed Video(s):     {len(anti_seed_urls_list)} negative example(s) configured (beta={anti_beta:.2f}, margin={anti_margin:.2f})")
        for idx, a_u in enumerate(anti_seed_urls_list, start=1):
            print(f"   [-] {a_u}")
    print(f" Output Directory:       {output_dir.resolve()}")
    print(f" Scratch Temp Dir:       {temp_dir.resolve()}")
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

    # 1. Initialize State, Embeddings & Cookie Session
    conn = init_database(db_path)
    engine = EmbeddingEngine(backend=embedding_backend)
    active_cookies = resolve_cookies(cookies_file=cookies_file, browser=browser_cookies)
    if active_cookies:
        print(f"[*] Cookie session active: {active_cookies.name}")
    else:
        print("[!] No cookie file available — running unauthenticated (bot-check risk).")

    # 2. Extract Seed Video(s) Info & Compute Normalized Seed Centroid
    print(f"\n[*] Step 1: Initializing {len(seed_urls_list)} Seed Video(s)...")

    ydl_meta: Any = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"node": {}},
    }
    if active_cookies:
        ydl_meta["cookiefile"] = str(active_cookies)

    seed_embeddings: List[np.ndarray] = []
    seed_entries: List[Dict[str, Any]] = []
    seed_errors: List[str] = []

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
            seed_errors.append(f"{s_url} -> {type(e).__name__}: {e}")
            print(f"  [!] Failed to extract seed {s_url}: {e}")

    if not seed_embeddings:
        err_details = "\n    - " + "\n    - ".join(seed_errors) if seed_errors else "Empty seed list."
        raise RuntimeError(f"No valid seed videos could be fetched or embedded. Aborting pipeline.\nDetailed causes:{err_details}")

    # Calculate Seed Centroid (mean of all normalized seed embeddings)
    seed_centroid = np.mean(seed_embeddings, axis=0)
    c_norm = np.linalg.norm(seed_centroid)
    if c_norm > 0:
        seed_embedding = seed_centroid / c_norm
    else:
        seed_embedding = seed_embeddings[0]

    print(f"[*] Computed Seed Centroid Vector across {len(seed_embeddings)} seed video(s).")

    # 2b. Extract Anti-Seed Video(s) & Compute Anti-Seed Centroid + Projection Matrix (Negative Anchor)
    anti_embeddings: List[np.ndarray] = []
    if anti_seed_urls_list:
        print(f"\n[*] Step 1b: Initializing {len(anti_seed_urls_list)} Anti-Seed Video(s) (Negative Anchor)...")
        for a_url in anti_seed_urls_list:
            try:
                a_id = extract_video_id(a_url)
                with yt_dlp.YoutubeDL(ydl_meta) as ydl:
                    a_info = ydl.extract_info(a_url, download=False)

                a_title = str(a_info.get("title") or "Anti-Seed Video").strip()
                # Use clean title for anti-seeds to prevent channel tags (e.g. "copacabana beach")
                # from polluting the negative anchor space.
                a_text = a_title
                a_emb = engine.embed(a_text)
                a_norm = np.linalg.norm(a_emb)
                if a_norm > 0:
                    a_emb = a_emb / a_norm
                anti_embeddings.append(a_emb)
                print(f"  [-] Seed ({a_id}): {a_title[:50]}")
            except Exception as e:
                print(f"  [!] Failed to extract anti-seed {a_url}: {e}")

    anti_embedding: Optional[np.ndarray] = None
    anti_matrix: Optional[np.ndarray] = None
    if anti_embeddings:
        anti_matrix = np.array(anti_embeddings, dtype=np.float32)
        anti_centroid = np.mean(anti_embeddings, axis=0)
        a_norm = np.linalg.norm(anti_centroid)
        anti_embedding = anti_centroid / a_norm if a_norm > 0 else anti_embeddings[0]
        print(f"[*] Computed Anti-Seed Centroid Vector across {len(anti_embeddings)} anti-seed(s).")

    # Pure positive centroid anchor (C+) decoupled from Rocchio repulsion
    pos_embedding: np.ndarray = seed_embedding.copy()

    # ref_embedding maintains the weighted anchor centroid:
    # If anti-seeds exist, apply Rocchio negative feedback: C* = normalize(C_pos - beta * C_anti)
    if anti_embedding is not None and anti_beta > 0.0:
        repelled = seed_embedding - (anti_beta * anti_embedding)
        r_norm = np.linalg.norm(repelled)
        ref_embedding = repelled / r_norm if r_norm > 0 else seed_embedding.copy()
        print(f"[*] Applied Rocchio Anti-Seed Repulsion (beta={anti_beta:.2f}) -> anchor tilted away from false positives.")
    else:
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
            for v in top_vids:
                t_vid = v.get("id")
                if not t_vid or is_video_seen(conn, t_vid) or t_vid in queued_video_ids:
                    continue
                v_title_entry = v.get("title", "Untitled")
                is_valid, v_sim, v_anti = evaluate_video_similarity(
                    title=v_title_entry,
                    reference_embedding=ref_embedding,
                    engine=engine,
                    pos_embedding=pos_embedding,
                    anti_embedding=anti_embedding,
                    anti_matrix=anti_matrix,
                    min_score=min_video_similarity,
                    anti_margin=anti_margin,
                )
                if not is_valid:
                    if (anti_embedding is not None or anti_matrix is not None) and v_sim >= min_video_similarity:
                        v_url = v.get("url") or f"https://www.youtube.com/watch?v={t_vid}"
                        print(f"    [-] Rejected false positive: {v_title_entry[:45]} {v_url} (pos={v_sim:.2f}, anti={v_anti:.2f})")
                    continue

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
                    merged_video_path = harvest_video_merged(
                        video_url=v_url,
                        video_id=v_id,
                        channel_id=v_ch_id or v_ch_name,
                        channel_name=v_ch_name,
                        video_title=v_title,
                        peaks=peaks,
                        output_dir=output_dir,
                        conn=conn,
                        clip_format=clip_format,
                        cookies_file=active_cookies,
                        video_similarity=v_sim,
                        temp_dir=temp_dir,
                    )
                    if merged_video_path:
                        total_clips_harvested += len(peaks)
                        try:
                            rel_display = merged_video_path.relative_to(output_dir)
                        except Exception:
                            rel_display = merged_video_path.name
                        print(f"         [✓] Harvested & merged {len(peaks)} clips into: {rel_display} (1x native speed | Total clips: {total_clips_harvested})")
                        record_video(conn, v_id, v_ch_url, v_title, "processed", True, similarity=v_sim)
                    else:
                        print(f"         [!] Failed to harvest and merge video {v_id}")
                        record_video(conn, v_id, v_ch_url, v_title, "error_harvesting", False, similarity=v_sim)
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
                    pos_embedding=pos_embedding,
                    anti_embedding=anti_embedding,
                    anti_matrix=anti_matrix,
                    top_limit=top_n_channel_videos,
                    anti_margin=anti_margin,
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
                    pos_embedding = blended / b_norm if b_norm > 0 else seed_embedding.copy()

                    if anti_embedding is not None and anti_beta > 0.0:
                        repelled = pos_embedding - (anti_beta * anti_embedding)
                        r_norm = np.linalg.norm(repelled)
                        ref_embedding = repelled / r_norm if r_norm > 0 else pos_embedding.copy()
                    else:
                        ref_embedding = pos_embedding.copy()

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
                    is_valid, v_sim, v_anti = evaluate_video_similarity(
                        title=v_title_entry,
                        reference_embedding=ref_embedding,
                        engine=engine,
                        pos_embedding=pos_embedding,
                        anti_embedding=anti_embedding,
                        anti_matrix=anti_matrix,
                        min_score=min_video_similarity,
                        anti_margin=anti_margin,
                    )
                    entry["similarity_score"] = round(v_sim, 4)

                    if not is_valid:
                        if (anti_embedding is not None or anti_matrix is not None) and v_sim >= min_video_similarity:
                            print(f"      [-] Rejected Anti-Seed False Positive: {v_title_entry[:45]} (pos={v_sim:.2f}, anti={v_anti:.2f})")
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
                    anti_tag = f" | anti={v_anti:.2f}" if (anti_embedding is not None or anti_matrix is not None) else ""
                    print(f"({idx}/{tot_candidates}) [POOL #{enqueued_count}] {v_sim:.2f}{anti_tag} | {v_title_entry[:45]} | {v_link}")

            # Case 3: Also check the triggering recommended video itself
            rec_vid = cand_meta.get("video_id")
            if rec_vid and not is_video_seen(conn, rec_vid) and rec_vid not in queued_video_ids:
                rec_title = str(cand_meta.get("title") or "")
                is_valid, rec_sim, rec_anti = evaluate_video_similarity(
                    title=rec_title,
                    reference_embedding=ref_embedding,
                    engine=engine,
                    pos_embedding=pos_embedding,
                    anti_embedding=anti_embedding,
                    anti_matrix=anti_matrix,
                    min_score=min_video_similarity,
                    anti_margin=anti_margin,
                )
                if is_valid:
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
                    anti_tag = f" (anti: {rec_anti:.2f})" if (anti_embedding is not None or anti_matrix is not None) else ""
                    print(f"      [+] Discovered candidate from approved channel ({rec_sim:.2f}{anti_tag}): {rec_title[:55]} ({rec_vid})")
                elif (anti_embedding is not None or anti_matrix is not None) and rec_sim >= min_video_similarity and (rec_sim - rec_anti) <= anti_margin:
                    print(f"      [-] Rejected candidate false positive: {rec_title[:50]} (pos={rec_sim:.2f}, anti={rec_anti:.2f})")

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

    # Display Top 5 Clips by Global Rank Index (GRI = Prominence * Z-Score * Similarity)
    try:
        top_clips = conn.execute("""
            SELECT clip_id, prominence, z_score, global_rank_index, file_path
            FROM clips
            WHERE global_rank_index IS NOT NULL
            ORDER BY global_rank_index DESC
            LIMIT 5
        """).fetchall()
        if top_clips:
            print("\n Top 5 Clips Ranked Globally (GRI = Prominence * Z-Score * Similarity):")
            for rank_i, tc in enumerate(top_clips, start=1):
                c_fn = Path(tc[4]).name if tc[4] else tc[0]
                gri_v = tc[3] if tc[3] is not None else 0.0
                print(f"   #{rank_i} GRI: {gri_v:.3f} (Prom {tc[1]:.2f}, Z {tc[2]:.2f}) -> {c_fn}")
            print("=" * 70)
    except Exception as e:
        pass

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
    parser.add_argument("--cookies-file", default=None, help="Path to Netscape cookies.txt file for YouTube authentication")
    parser.add_argument("--browser-cookies", default=DEFAULT_BROWSER_COOKIES, help="Browser to extract cookies from if no cookies file is found (firefox, chrome, etc.)")
    parser.add_argument("--anti-seed", default=None, help="Anti-seed video URL or comma-separated list of URLs to repel false positives")
    parser.add_argument("--anti-beta", type=float, default=DEFAULT_ANTI_SEED_BETA, help=f"Rocchio anti-seed repulsion factor (default: {DEFAULT_ANTI_SEED_BETA:.2f})")
    parser.add_argument("--anti-margin", type=float, default=DEFAULT_ANTI_SEED_MARGIN, help=f"Contrastive margin guardrail: sim_pos - sim_anti > margin (default: {DEFAULT_ANTI_SEED_MARGIN:.2f})")
    parser.add_argument("--temp-dir", default=str(DEFAULT_TEMP_DIR), help=f"Scratch temporary directory for intermediate encodes (default: {DEFAULT_TEMP_DIR})")
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

    # Sanity assert: Rocchio Anti-Seed Repulsion tilts reference away from negative subspace
    v_pos = np.array([1.0, 0.0])
    v_neg = np.array([0.7071, 0.7071])  # Correlated false positive
    v_rep = v_pos - DEFAULT_ANTI_SEED_BETA * v_neg
    v_rep = v_rep / np.linalg.norm(v_rep)
    assert np.isclose(np.linalg.norm(v_rep), 1.0)
    assert float(np.dot(v_rep, v_neg)) < float(np.dot(v_pos, v_neg)), "Repulsion must penalize negative direction"

    # Sanity assert: Contrastive Margin Guardrail rejects candidate closer to anti-seeds
    v_cand_fp = np.array([0.7071, 0.7071])
    v_anti_matrix = np.array([[0.7071, 0.7071], [0.0, 1.0]])
    sim_pos = float(np.dot(v_rep, v_cand_fp))
    sim_anti_max = float(np.max(np.dot(v_anti_matrix, v_cand_fp)))
    assert sim_anti_max >= sim_pos, "Candidate closer to anti-seeds must be rejected by guardrail"

    # Run the pipeline
    run_harvest_pipeline(
        seed_url=args.seed,
        output_dir=resolve_storage_path(args.output_dir),
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
        cookies_file=Path(args.cookies_file) if args.cookies_file else None,
        browser_cookies=args.browser_cookies,
        anti_seed_url=args.anti_seed,
        anti_beta=args.anti_beta,
        anti_margin=args.anti_margin,
        temp_dir=resolve_temp_dir(args.temp_dir),
    )


if __name__ == "__main__":
    main()
