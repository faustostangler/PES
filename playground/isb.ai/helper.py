"""Helper utilities shared across the playground modules."""

import re
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path


def clean_filename(name: str) -> str:
    """Clean entity name to create a safe, clean filename for Obsidian."""
    # Remove invalid characters for filenames: / \\ ? % * : | " < >
    cleaned = re.sub(r'[\\/*?:"<>|%]', "", name)
    return cleaned.strip()

def sanitize_for_path(name: str) -> str:
    """Sanitize a name (category, channel, etc.) to be safe for directory naming (snake_case)."""
    if not name:
        return "unknown"
    name = name.replace("&", " ")
    name = re.sub(r"[^a-zA-Z0-9\s_-]", " ", name)
    name = re.sub(r"[\s_-]+", "_", name).strip("_").lower()
    return name or "unknown"

def format_date_for_path(upload_date_str: str) -> str:
    """Format any upload date string (ISO or YYYYMMDD) into YYYY-MM-DD."""
    if not upload_date_str:
        return "unknown_date"
    try:
        if "-" in upload_date_str:
            return upload_date_str.split("T")[0]
        else:
            dt = datetime.strptime(upload_date_str, "%Y%m%d")
            return dt.strftime("%Y-%m-%d")
    except Exception:
        return "unknown_date"

import http.cookiejar
import threading

_COOKIE_JAR = None
_COOKIE_FILE_PATH = None
_COOKIE_LOCK = threading.Lock()


def get_cached_cookiefile() -> str | None:
    """Extract browser cookies ONCE into a static Netscape cookies file to eliminate SQLite DB locking across thread pools."""
    global _COOKIE_JAR, _COOKIE_FILE_PATH
    with _COOKIE_LOCK:
        if _COOKIE_FILE_PATH is not None:
            return _COOKIE_FILE_PATH if _COOKIE_FILE_PATH != "" else None

        cookie_file = Path(__file__).parent / ".yt_dlp_cookies.txt"
        
        # If valid cookiefile already exists and has content, load it directly
        if cookie_file.exists() and cookie_file.stat().st_size > 50:
            try:
                mcj = http.cookiejar.MozillaCookieJar(str(cookie_file))
                mcj.load(ignore_discard=True, ignore_expires=True)
                _COOKIE_JAR = mcj
                _COOKIE_FILE_PATH = str(cookie_file)
                # print(f"✓ Using existing cookie file: {cookie_file.name}")
                return _COOKIE_FILE_PATH
            except Exception:
                pass

        tmp_cookie_file = cookie_file.with_suffix(".tmp")
        try:
            from yt_dlp.cookies import extract_cookies_from_browser
            
            # On Linux, Firefox does not lock behind OS keyrings, followed by Chrome
            browsers_to_try = ["firefox", "chrome", "chromium", "brave"]
            for browser_name in browsers_to_try:
                try:
                    cj = extract_cookies_from_browser(browser_name)
                except Exception:
                    continue

                if not cj:
                    continue

                mcj = http.cookiejar.MozillaCookieJar(str(tmp_cookie_file))
                count = 0
                for c in cj:
                    domain = (c.domain or "").lower()
                    if not (domain.endswith("youtube.com") or domain.endswith("google.com") or domain.endswith("ytimg.com")):
                        continue
                    if any(sub in domain for sub in ("takeout", "docs", "mail", "drive", "cloud", "meet", "chat", "play", "store", "admin", "sites", "groups", "photos")):
                        continue
                    if not c.name or not c.value or len(c.value.strip()) == 0:
                        continue
                    if len(c.name) > 200 or len(c.value) > 2000:
                        continue
                    if not re.match(r"^[!-~]+$", c.name) or not re.match(r"^[ -~]+$", c.value):
                        continue
                    if c.expires and c.expires > 2147483647:
                        c.expires = 2147483647
                    mcj.set_cookie(c)
                    count += 1

                if count > 0:
                    mcj.save(ignore_discard=True, ignore_expires=True)
                    tmp_cookie_file.replace(cookie_file)
                    _COOKIE_JAR = mcj
                    _COOKIE_FILE_PATH = str(cookie_file)
                    print(f"✓ Cookies extracted from {browser_name} to {cookie_file.name} ({count} clean YouTube/Google cookies)")
                    return _COOKIE_FILE_PATH

        except Exception as e:
            if tmp_cookie_file.exists():
                tmp_cookie_file.unlink(missing_ok=True)

        _COOKIE_JAR = None
        _COOKIE_FILE_PATH = ""
        return None


def apply_cookies_to_ydl_opts(ydl_opts: dict, use_cookies: bool = True) -> None:
    """Apply pre-extracted clean cookiefile to yt_dlp options."""
    if not use_cookies:
        return
    cookie_path = get_cached_cookiefile()
    if cookie_path and Path(cookie_path).exists() and Path(cookie_path).stat().st_size > 0:
        ydl_opts["cookiefile"] = cookie_path


def _get_chrome_cookies():
    global _COOKIE_JAR
    if _COOKIE_JAR is None and _COOKIE_FILE_PATH is None:
        get_cached_cookiefile()
    return _COOKIE_JAR if _COOKIE_JAR else None


def fetch_url_content(url: str, headers: dict | None = None, use_cookies: bool = False) -> str:
    """Fetch content of a URL as string with a user-agent header.

    Timedtext URLs are pre-signed by YouTube and will return HTTP 400 if attached with mismatched/corrupted cookies,
    so use_cookies defaults to False.
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    req = urllib.request.Request(url, headers=headers)

    handlers = []
    if use_cookies:
        cj = _get_chrome_cookies()
        if cj:
            handlers.append(urllib.request.HTTPCookieProcessor(cj))

    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        # If a request fails with 400 and cookies were used, retry without cookies
        if e.code == 400 and use_cookies:
            clean_opener = urllib.request.build_opener()
            with clean_opener.open(req, timeout=10) as response:
                return response.read().decode('utf-8')
        raise e

def get_full_upload_date(info: dict) -> str:
    """Retrieve full upload date if available (ISO timestamp), falling back to YYYYMMDD."""
    timestamp = info.get("timestamp")
    if timestamp:
        try:
            return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()
        except Exception:
            pass
    return info.get("upload_date", "")

def is_within_range(upload_date_str: str, days_limit: int) -> bool:
    """Check if the upload date string falls within the last X days."""
    if not upload_date_str:
        return False
    try:
        if "-" in upload_date_str:
            clean_str = upload_date_str.split("T")[0]
            upload_date = datetime.strptime(clean_str, "%Y-%m-%d").replace(tzinfo=UTC)
        else:
            upload_date = datetime.strptime(upload_date_str, "%Y%m%d").replace(tzinfo=UTC)

        threshold_date = datetime.now(UTC) - timedelta(days=days_limit)
        return upload_date >= threshold_date
    except Exception:
        return False

def read_playlist_urls(file_path: Path) -> list[str]:
    """Read seed video URLs from a text file, skipping comments and blank lines."""
    urls = []
    if file_path.exists():
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                if "#" in line:
                    continue
                line = line.strip()
                if line:
                    urls.append(line)
    return urls

def parse_merged_transcriptions(file_path: Path) -> list[dict]:
    """Parse a file containing multiple transcription blocks separated by --- blocks.

    Each block contains a dictionary of metadata and the corresponding text.
    """
    metadata_list = []
    if not file_path.exists():
        return metadata_list
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by lines containing only '---'
        parts = re.split(r"^---$", content, flags=re.MULTILINE)

        # Alternating: parts[1] is YAML, parts[2] is transcript, parts[3] is YAML, parts[4] is transcript...
        i = 1
        while i < len(parts):
            yaml_text = parts[i]
            text_content = parts[i+1].strip() if i + 1 < len(parts) else ""

            meta = {}
            lines = yaml_text.splitlines()
            in_desc = False
            desc_lines = []

            for line in lines:
                if in_desc:
                    if line.startswith("  ") or line.strip() == "":
                        desc_lines.append(line[2:] if line.startswith("  ") else line)
                    else:
                        in_desc = False

                if in_desc:
                    continue
                if ":" not in line:
                    continue
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if key == "video_description":
                    in_desc = True
                    continue
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                meta[key] = val

            if desc_lines:
                meta["video_description"] = "\n".join(desc_lines)

            metadata_list.append({
                "metadata": meta,
                "text": text_content
            })
            i += 2
    except Exception as e:
        print(f"Error parsing merged transcriptions in {file_path.name}: {e}")
    return metadata_list


def parse_yaml_header(file_path: Path) -> dict:
    """Read the YAML frontmatter block at the top of a file (between first two ---)."""
    blocks = parse_merged_transcriptions(file_path)
    return blocks[0]["metadata"] if blocks else {}


def extract_youtube_video_id(url: str) -> str | None:
    """Extract 11-character video ID from various YouTube URL formats."""
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|v/|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None
