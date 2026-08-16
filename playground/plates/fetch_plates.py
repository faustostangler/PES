#!/usr/bin/env python3
"""Scrape and standardize license plate images from 15q.net for all US states."""

import argparse
import re
import sys
import time
import urllib.parse
from pathlib import Path
import requests

# --- Config ---
BASE_URL = "http://15q.net"
OUTPUT_DIR = Path("downloads")
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
TIMEOUT = 30
REQUEST_DELAY = 0.3  # Polite delay between requests to prevent throttling
MAX_RETRIES = 3

# All 50 US states + DC
STATES = [
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "dc", "fl",
    "ga", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me",
    "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh",
    "nj", "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri",
    "sc", "sd", "tn", "tx", "ut", "vt", "va", "wv", "wa", "wi",
    "wy"
]


# --- Logic ---
def standardize_filename(filename: str) -> str:
    """Standardize plate filename to 4-digit year-first convention.

    Format conversion:
    - 'al69.jpg'  -> '1969-al-1.jpg'
    - 'al69a.jpg' -> '1969-al-2.jpg'
    - 'al69b.jpg' -> '1969-al-3.jpg'
    - 'ca01.jpg'  -> '2001-ca-1.jpg'
    - 'ny02c.jpg' -> '2002-ny-4.jpg'
    - 'al27.jpg'  -> '1927-al-1.jpg'
    - 'al06.jpg'  -> '2006-al-1.jpg'
    - 'al26.jpg'  -> '2026-al-1.jpg'

    >>> standardize_filename('al69.jpg')
    '1969-al-1.jpg'
    >>> standardize_filename('al69a.jpg')
    '1969-al-2.jpg'
    >>> standardize_filename('al69b.jpg')
    '1969-al-3.jpg'
    >>> standardize_filename('ca01.jpg')
    '2001-ca-1.jpg'
    >>> standardize_filename('ny02c.jpeg')
    '2002-ny-4.jpg'
    >>> standardize_filename('al27.jpg')
    '1927-al-1.jpg'
    >>> standardize_filename('al06.jpg')
    '2006-al-1.jpg'
    """
    base_name = filename.split("/")[-1]
    match = re.match(r"^([a-zA-Z]{2})(\d{2})([a-zA-Z]?)\.(jpe?g)$", base_name, re.IGNORECASE)
    if not match:
        return base_name

    state, year, suffix, _ = match.groups()
    state = state.lower()

    # 4-digit year calculation: > 26 -> 19xx, <= 26 -> 20xx
    yr_int = int(year)
    full_year = f"19{year}" if yr_int > 30 else f"20{year}"

    if not suffix:
        index = 1
    else:
        index = ord(suffix.lower()) - ord("a") + 2

    return f"{full_year}-{state}-{index}.jpg"


def create_session() -> requests.Session:
    """Create a persistent requests session with browser headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    return session


def fetch_with_retry(session: requests.Session, url: str, retries: int = MAX_RETRIES) -> requests.Response:
    """Fetch URL with retries and exponential backoff."""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(attempt * 2.0)
    raise last_err or RuntimeError(f"Failed to fetch {url}")


def find_plate_images(html_content: str, state_code: str, page_url: str) -> list[tuple[str, str, str]]:
    """Parse HTML and extract (original_filename, full_image_url, standardized_filename)."""
    raw_matches = re.findall(r'(?:href|src)=[\"\']?([^\s\"\'><]+\.jpe?g)', html_content, re.IGNORECASE)
    
    seen_urls = set()
    plate_items = []
    pattern = re.compile(rf"^({state_code})(\d{{2}})([a-zA-Z]?)\.(jpe?g)$", re.IGNORECASE)

    for raw_path in raw_matches:
        filename = raw_path.split("/")[-1]
        if pattern.match(filename):
            full_url = urllib.parse.urljoin(page_url, raw_path)
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                std_filename = standardize_filename(filename)
                plate_items.append((filename, full_url, std_filename))

    return plate_items


def download_image(session: requests.Session, url: str, dest_path: Path) -> bool:
    """Download image to destination path if not already downloaded."""
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return True

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = fetch_with_retry(session, url)
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception as e:
        print(f"    [!] Error downloading {url}: {e}")
        return False


def format_time(seconds: float) -> str:
    """Format seconds into hh:mm:ss string.

    >>> format_time(3665)
    '01:01:05'
    >>> format_time(59)
    '00:00:59'
    """
    total_sec = max(0, int(seconds))
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def process_state(session: requests.Session, state: str, output_dir: Path, download: bool = True, delay: float = REQUEST_DELAY) -> list[tuple[str, str, str]]:
    """Fetch page for a single state, extract plates and download them."""
    page_url = f"{BASE_URL}/{state}.html"
    try:
        resp = fetch_with_retry(session, page_url)
        plates = find_plate_images(resp.text, state, page_url)
        print(f"[+] {state.upper()}: Found {len(plates)} plate images from {page_url}")

        if download and plates:
            downloaded = 0
            start_time = time.time()
            total_count = len(plates)

            for idx, (orig_fn, img_url, std_fn) in enumerate(plates, 1):
                save_path = output_dir / std_fn
                if download_image(session, img_url, save_path):
                    downloaded += 1

                elapsed = time.time() - start_time
                avg_time = elapsed / idx
                remaining = avg_time * (total_count - idx)
                total_est = elapsed + remaining
                timer_str = f"{format_time(elapsed)}+{format_time(remaining)} = {format_time(total_est)}"

                print(f"    [{idx:02d}/{total_count:02d}] {std_fn} | ETA: {timer_str}", flush=True)

                if delay > 0:
                    time.sleep(delay)

            total_elapsed = time.time() - start_time
            print(f"    -> Saved {downloaded}/{total_count} images to {output_dir}/ in {format_time(total_elapsed)}")

        return plates
    except Exception as e:
        print(f"[-] {state.upper()}: Failed to process {page_url} ({e})")
        return []


def run(states: list[str], output_dir: Path, download: bool = True, delay: float = REQUEST_DELAY):
    """Run extraction across specified states."""
    output_dir.mkdir(parents=True, exist_ok=True)
    session = create_session()

    print(f"Starting 15q.net plate scraper for {len(states)} state(s)...")
    print(f"Output directory: {output_dir.resolve()}")
    print(f"Download enabled: {download}\n")

    total_plates = 0
    start_time = time.time()
    total_states = len(states)

    for idx, state in enumerate(states, 1):
        elapsed = time.time() - start_time
        if idx > 1:
            avg_time = elapsed / (idx - 1)
            remaining = avg_time * (total_states - (idx - 1))
            total_est = elapsed + remaining
            eta_str = f" | Overall ETA: {format_time(elapsed)}+{format_time(remaining)} = {format_time(total_est)}"
        else:
            eta_str = ""

        print(f"\n[{idx:02d}/{total_states:02d}] Processing state '{state.upper()}'{eta_str}")
        plates = process_state(session, state, output_dir, download=download, delay=delay)
        total_plates += len(plates)
        if delay > 0 and idx < total_states:
            time.sleep(delay)

    total_elapsed = time.time() - start_time
    print(f"\n[DONE] Processed {total_states} state(s) in {format_time(total_elapsed)}. Total plate images found: {total_plates}")


# --- Main ---
if __name__ == "__main__":
    import doctest

    # Inline tests and sanity asserts
    doctest_result = doctest.testmod()
    assert doctest_result.failed == 0, f"Doctests failed: {doctest_result}"
    assert standardize_filename("al69.jpg") == "1969-al-1.jpg"
    assert standardize_filename("al69a.jpg") == "1969-al-2.jpg"
    assert standardize_filename("al69b.jpg") == "1969-al-3.jpg"
    assert standardize_filename("al27.jpg") == "1927-al-1.jpg"
    assert standardize_filename("al06.jpg") == "2006-al-1.jpg"
    assert standardize_filename("al26.jpg") == "2026-al-1.jpg"

    parser = argparse.ArgumentParser(description="Scrape license plate images from 15q.net.")
    parser.add_argument("--state", type=str, help="Specific state code to scrape (e.g. 'al', 'ca'). Default: all states.")
    parser.add_argument("--no-download", action="store_true", help="Only parse and list images without downloading.")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR, help="Destination directory for downloads.")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY, help="Delay (seconds) between HTTP requests.")
    args = parser.parse_args()

    selected_states = [args.state.lower()] if args.state else STATES
    run(selected_states, args.output, download=not args.no_download, delay=args.delay)
