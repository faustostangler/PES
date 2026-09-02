#!/usr/bin/env python3
"""Scrape Bend (bend.com/routines) routines and exercises into SQLite, JSON, and CSV databases.

Fast, concurrent scraper following the stangler-fast methodology.
Extracts all routines, categorizes them, extracts all exercises with images,
instructions, tips, modifications, and benefits lists.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import re
import sqlite3
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

# --- Configuration Constants ---
BASE_URL = "https://bend.com"
ROUTINES_URL = f"{BASE_URL}/routines"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
DEFAULT_WORKERS = 10
DEFAULT_TIMEOUT = 20


def build_http_session(workers: int) -> requests.Session:
    """Create a thread-safe requests session with connection pooling and retries."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        pool_connections=workers * 2,
        pool_maxsize=workers * 2,
        max_retries=retries,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def clean_image_url(raw_url: str) -> str:
    """Extract direct high-res image URL from Next.js image proxy url if present."""
    if not raw_url:
        return ""
    if "_next/image" in raw_url:
        match = re.search(r"url=([^&]+)", raw_url)
        if match:
            return urllib.parse.unquote(match.group(1))
    if raw_url.startswith("/"):
        return f"{BASE_URL}{raw_url}"
    return raw_url


def parse_duration_seconds(duration_str: str) -> int:
    """Parse string like '1:00' or '0:30' or 'PT60S' into total seconds."""
    if not duration_str:
        return 0
    if duration_str.startswith("PT") and duration_str.endswith("S"):
        try:
            return int(duration_str[2:-1])
        except ValueError:
            pass
    parts = duration_str.split(":")
    if len(parts) == 2:
        try:
            return int(parts[0]) * 60 + int(parts[1])
        except ValueError:
            return 0
    return 0


def categorize_routine(slug: str, title: str) -> str:
    """Classify routine into logical categories based on slug and title."""
    s = f"{slug.lower()} {title.lower()}"
    if "pelvic" in s:
        return "Pelvic Floor"
    if "hips" in s:
        return "Hips"
    if "lower-back" in s or "lower back" in s:
        return "Lower Back"
    if "hamstring" in s:
        return "Hamstrings"
    if "shoulder" in s:
        return "Shoulders"
    if "chest" in s:
        return "Chest"
    if "neck" in s:
        return "Neck"
    if "quad" in s:
        return "Quads"
    if any(k in s for k in ["core", "abs", "plank"]):
        return "Core & Abs"
    if any(k in s for k in ["upper-body", "upper body", "arms", "back"]):
        return "Upper Body"
    if any(k in s for k in ["lower-body", "lower body", "feet", "ankle", "squat"]):
        return "Lower Body"
    if "full-body" in s or "full body" in s:
        return "Full Body"
    if "split" in s:
        return "Splits"
    if "run" in s:
        return "Running"
    if "posture" in s:
        return "Posture"
    if any(k in s for k in ["wake", "morning"]):
        return "Morning"
    if any(k in s for k in ["sleep", "relax"]):
        return "Evening & Relaxation"
    if "desk" in s:
        return "Desk & Work"
    return "Flexibility & Flow"


def get_all_routine_slugs(session: requests.Session) -> list[dict[str, str]]:
    """Discover all routine URLs from /routines and sitemap.xml."""
    resp = session.get(ROUTINES_URL, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    
    routines_map: dict[str, dict[str, str]] = {}
    
    for li in soup.find_all("li"):
        a = li.find("a", href=re.compile(r"^/routines/[a-z0-9\-]+$"))
        if a:
            slug = a["href"].split("/")[-1]
            h3 = a.find("h3")
            time_el = a.find("time")
            img = a.find("img")
            
            thumb_url = clean_image_url(img.get("src", "")) if img else ""
            title = h3.get_text(strip=True) if h3 else slug.replace("-", " ").title()
            duration = time_el.get_text(strip=True) if time_el else ""
            
            routines_map[slug] = {
                "slug": slug,
                "url": f"{BASE_URL}/routines/{slug}",
                "title": title,
                "duration": duration,
                "thumbnail_url": thumb_url,
                "category": categorize_routine(slug, title),
            }
            
    # Supplement from sitemap.xml in case any routine was missing
    try:
        sitemap_resp = session.get(SITEMAP_URL, timeout=DEFAULT_TIMEOUT)
        if sitemap_resp.status_code == 200:
            sitemap_slugs = re.findall(r"https://bend\.com/routines/([a-z0-9\-]+)", sitemap_resp.text)
            for slug in sitemap_slugs:
                if slug not in routines_map:
                    routines_map[slug] = {
                        "slug": slug,
                        "url": f"{BASE_URL}/routines/{slug}",
                        "title": slug.replace("-", " ").title(),
                        "duration": "",
                        "thumbnail_url": "",
                        "category": categorize_routine(slug, slug),
                    }
    except Exception as exc:
        print(f"Warning: could not check sitemap: {exc}", file=sys.stderr)
        
    return list(routines_map.values())


def scrape_routine_page(session: requests.Session, routine_meta: dict[str, str]) -> dict[str, Any]:
    """Scrape a single routine page and extract overview + exercise instructions."""
    url = routine_meta["url"]
    slug = routine_meta["slug"]
    resp = session.get(url, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    
    # 1. Title & Description
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else routine_meta.get("title", "")
    
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
    
    # Duration from page header if available
    header_block = h1.parent if h1 else None
    duration = routine_meta.get("duration", "")
    if header_block:
        time_tag = header_block.find("time")
        if time_tag:
            duration = time_tag.get_text(strip=True)
            
    # 2. Exercise Overview (ordered list with durations)
    overview_map: list[dict[str, Any]] = []
    ov_heading = soup.find(lambda el: el.name == "h2" and "Exercise Overview" in el.text)
    if ov_heading and ov_heading.parent:
        for li in ov_heading.parent.find_all("li"):
            name_span = li.find("span", class_=lambda c: c and "font-medium" in c)
            time_el = li.find("time")
            img_el = li.find("img")
            
            ex_name = name_span.get_text(strip=True) if name_span else ""
            dur_text = time_el.get_text(strip=True) if time_el else ""
            dur_datetime = time_el.get("datetime", "") if time_el else ""
            dur_sec = parse_duration_seconds(dur_datetime or dur_text)
            thumb = clean_image_url(img_el.get("src", "")) if img_el else ""
            
            if ex_name:
                overview_map.append({
                    "name": ex_name,
                    "duration": dur_text,
                    "duration_seconds": dur_sec,
                    "thumbnail_url": thumb,
                })
                
    # 3. Exercise Instructions articles
    exercises_data: list[dict[str, Any]] = []
    instr_heading = soup.find(lambda el: el.name == "h2" and "Exercise Instructions" in el.text)
    if instr_heading and instr_heading.parent:
        articles = instr_heading.parent.find_all("article")
        for idx, art in enumerate(articles, start=1):
            h3 = art.find("h3")
            raw_title = h3.get_text(" ", strip=True) if h3 else f"Exercise {idx}"
            # Clean "1 . Lunge" -> "Lunge"
            clean_name = re.sub(r"^\s*\d+\s*[\.\-]?\s*", "", raw_title).strip()
            
            # Figure / Image
            img = art.find("img")
            image_url = clean_image_url(img.get("src", "")) if img else ""
            alt_text = img.get("alt", "") if img else ""
            
            # Sections: Instructions, Tips, Modifications, Benefits
            instructions: list[str] = []
            tips: list[str] = []
            modifications: list[str] = []
            benefits: list[str] = []
            
            for sec in art.find_all("section"):
                sec_h = sec.find(["h4", "h5", "h6"])
                if not sec_h:
                    continue
                header_text = sec_h.get_text(strip=True).lower()
                
                # List items
                items = [li.get_text(" ", strip=True) for li in sec.find_all("li")]
                
                if "instruction" in header_text:
                    instructions = items
                elif "tip" in header_text:
                    tips = items
                elif "modification" in header_text:
                    modifications = items
                elif "benefit" in header_text:
                    p = sec.find("p")
                    if p:
                        # e.g. "Abdomen, Hips, Lower Back, Psoas, Quadriceps"
                        benefits = [b.strip() for b in p.get_text(strip=True).split(",") if b.strip()]
                    elif items:
                        benefits = items
                        
            # Lookup overview duration if matching index or name
            ex_duration = ""
            ex_duration_sec = 0
            if idx - 1 < len(overview_map):
                ov_item = overview_map[idx - 1]
                ex_duration = ov_item["duration"]
                ex_duration_sec = ov_item["duration_seconds"]
            else:
                for ov_item in overview_map:
                    if ov_item["name"].lower() == clean_name.lower():
                        ex_duration = ov_item["duration"]
                        ex_duration_sec = ov_item["duration_seconds"]
                        break
                        
            exercises_data.append({
                "order": idx,
                "name": clean_name,
                "image_url": image_url,
                "alt_text": alt_text,
                "duration": ex_duration,
                "duration_seconds": ex_duration_sec,
                "instructions": instructions,
                "tips": tips,
                "modifications": modifications,
                "benefits": benefits,
            })
            
    return {
        "slug": slug,
        "name": title,
        "url": url,
        "category": routine_meta["category"],
        "description": desc,
        "duration": duration,
        "thumbnail_url": routine_meta.get("thumbnail_url", ""),
        "exercise_count": len(exercises_data),
        "exercises": exercises_data,
    }


def build_databases(
    routines: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Aggregate exercises across all routines and save to SQLite, JSON, and CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Aggregate Unique Exercises
    exercises_db: dict[str, dict[str, Any]] = {}
    
    for r in routines:
        routine_name = r["name"]
        routine_slug = r["slug"]
        routine_category = r["category"]
        
        for ex in r["exercises"]:
            name = ex["name"]
            if not name:
                continue
                
            if name not in exercises_db:
                exercises_db[name] = {
                    "name": name,
                    "slug": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
                    "image_url": ex["image_url"],
                    "alt_text": ex["alt_text"],
                    "instructions": ex["instructions"],
                    "tips": ex["tips"],
                    "modifications": ex["modifications"],
                    "benefits": ex["benefits"],
                    "routines": [],
                    "routine_slugs": [],
                    "categories": set(),
                }
            else:
                # Merge more complete fields if missing
                cur = exercises_db[name]
                if not cur["image_url"] and ex["image_url"]:
                    cur["image_url"] = ex["image_url"]
                if not cur["instructions"] and ex["instructions"]:
                    cur["instructions"] = ex["instructions"]
                if not cur["tips"] and ex["tips"]:
                    cur["tips"] = ex["tips"]
                if not cur["modifications"] and ex["modifications"]:
                    cur["modifications"] = ex["modifications"]
                if not cur["benefits"] and ex["benefits"]:
                    cur["benefits"] = ex["benefits"]
                    
            if routine_name not in exercises_db[name]["routines"]:
                exercises_db[name]["routines"].append(routine_name)
                exercises_db[name]["routine_slugs"].append(routine_slug)
            exercises_db[name]["categories"].add(routine_category)
            
    # Convert sets to sorted lists for JSON serialization
    for ex in exercises_db.values():
        ex["categories"] = sorted(list(ex["categories"]))
        ex["routine_count"] = len(ex["routines"])
        
    # 2. Categories Grouping
    categories_db: dict[str, dict[str, Any]] = {}
    for r in routines:
        cat = r["category"]
        if cat not in categories_db:
            categories_db[cat] = {
                "category": cat,
                "routine_count": 0,
                "routines": [],
                "unique_exercises": set(),
            }
        categories_db[cat]["routine_count"] += 1
        categories_db[cat]["routines"].append({
            "slug": r["slug"],
            "name": r["name"],
            "duration": r["duration"],
            "description": r["description"],
            "exercise_count": r["exercise_count"],
        })
        for ex in r["exercises"]:
            categories_db[cat]["unique_exercises"].add(ex["name"])
            
    for cat_data in categories_db.values():
        cat_data["unique_exercises"] = sorted(list(cat_data["unique_exercises"]))
        cat_data["exercise_count"] = len(cat_data["unique_exercises"])
        
    # 3. Build routine_exercises and benefits normalized datasets
    routine_exercises_data: list[dict[str, Any]] = []
    for r in routines:
        for ex in r["exercises"]:
            routine_exercises_data.append({
                "routine_slug": r["slug"],
                "routine_name": r["name"],
                "routine_category": r["category"],
                "exercise_order": ex["order"],
                "exercise_name": ex["name"],
                "duration": ex.get("duration", ""),
                "duration_seconds": ex.get("duration_seconds", 0),
            })

    exercise_benefits_data: list[dict[str, str]] = []
    for ex in exercises_db.values():
        for b in ex["benefits"]:
            exercise_benefits_data.append({
                "exercise_name": ex["name"],
                "benefit": b,
            })

    # --- Write JSON Files ---
    json_routines_path = output_dir / "routines.json"
    with open(json_routines_path, "w", encoding="utf-8") as f:
        json.dump(routines, f, indent=2, ensure_ascii=False)
        
    json_exercises_path = output_dir / "exercises.json"
    with open(json_exercises_path, "w", encoding="utf-8") as f:
        json.dump(list(exercises_db.values()), f, indent=2, ensure_ascii=False)
        
    json_categories_path = output_dir / "categories.json"
    with open(json_categories_path, "w", encoding="utf-8") as f:
        json.dump(categories_db, f, indent=2, ensure_ascii=False)

    json_routine_exercises_path = output_dir / "routine_exercises.json"
    with open(json_routine_exercises_path, "w", encoding="utf-8") as f:
        json.dump(routine_exercises_data, f, indent=2, ensure_ascii=False)

    json_exercise_order_path = output_dir / "exercise_order.json"
    with open(json_exercise_order_path, "w", encoding="utf-8") as f:
        json.dump(routine_exercises_data, f, indent=2, ensure_ascii=False)

    json_benefits_path = output_dir / "exercise_benefits.json"
    with open(json_benefits_path, "w", encoding="utf-8") as f:
        json.dump(exercise_benefits_data, f, indent=2, ensure_ascii=False)

    # --- Write CSV Files ---
    csv_exercises_path = output_dir / "exercises.csv"
    with open(csv_exercises_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name",
            "slug",
            "image_url",
            "alt_text",
            "benefits",
            "instructions",
            "tips",
            "modifications",
            "routine_count",
            "routines",
            "categories",
        ])
        for ex in sorted(exercises_db.values(), key=lambda x: x["name"]):
            writer.writerow([
                ex["name"],
                ex["slug"],
                ex["image_url"],
                ex.get("alt_text", ""),
                "; ".join(ex["benefits"]),
                " | ".join(ex["instructions"]),
                " | ".join(ex["tips"]),
                " | ".join(ex["modifications"]),
                ex["routine_count"],
                "; ".join(ex["routines"]),
                "; ".join(ex["categories"]),
            ])
            
    csv_routines_path = output_dir / "routines.csv"
    with open(csv_routines_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "slug",
            "name",
            "category",
            "duration",
            "exercise_count",
            "description",
            "url",
            "thumbnail_url",
            "exercise_names",
        ])
        for r in routines:
            ex_names = [ex["name"] for ex in r["exercises"]]
            writer.writerow([
                r["slug"],
                r["name"],
                r["category"],
                r["duration"],
                r["exercise_count"],
                r["description"],
                r["url"],
                r["thumbnail_url"],
                "; ".join(ex_names),
            ])

    csv_routine_exercises_path = output_dir / "routine_exercises.csv"
    with open(csv_routine_exercises_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "routine_slug",
            "routine_name",
            "routine_category",
            "exercise_order",
            "exercise_name",
            "duration",
            "duration_seconds",
        ])
        for row in routine_exercises_data:
            writer.writerow([
                row["routine_slug"],
                row["routine_name"],
                row["routine_category"],
                row["exercise_order"],
                row["exercise_name"],
                row["duration"],
                row["duration_seconds"],
            ])

    csv_exercise_order_path = output_dir / "exercise_order.csv"
    with open(csv_exercise_order_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "routine_slug",
            "routine_name",
            "routine_category",
            "exercise_order",
            "exercise_name",
            "duration",
            "duration_seconds",
        ])
        for row in routine_exercises_data:
            writer.writerow([
                row["routine_slug"],
                row["routine_name"],
                row["routine_category"],
                row["exercise_order"],
                row["exercise_name"],
                row["duration"],
                row["duration_seconds"],
            ])

    csv_categories_path = output_dir / "categories.csv"
    with open(csv_categories_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "routine_count", "exercise_count"])
        for cat_name, cat_obj in sorted(categories_db.items(), key=lambda x: x[0]):
            writer.writerow([cat_name, cat_obj["routine_count"], cat_obj["exercise_count"]])

    csv_benefits_path = output_dir / "exercise_benefits.csv"
    with open(csv_benefits_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["exercise_name", "benefit"])
        for row in exercise_benefits_data:
            writer.writerow([row["exercise_name"], row["benefit"]])

    # --- Write SQLite Database ---
    db_path = output_dir / "bend.db"
    if db_path.exists():
        db_path.unlink()
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE routines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            duration TEXT,
            description TEXT,
            url TEXT,
            thumbnail_url TEXT,
            exercise_count INTEGER NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            slug TEXT NOT NULL,
            image_url TEXT,
            alt_text TEXT,
            instructions_json TEXT,
            tips_json TEXT,
            modifications_json TEXT,
            benefits_json TEXT,
            routine_count INTEGER NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE routine_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            routine_slug TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            exercise_order INTEGER NOT NULL,
            duration TEXT,
            duration_seconds INTEGER,
            FOREIGN KEY (routine_slug) REFERENCES routines (slug),
            FOREIGN KEY (exercise_name) REFERENCES exercises (name)
        )
    """)
    
    cur.execute("""
        CREATE TABLE exercise_benefits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT NOT NULL,
            benefit TEXT NOT NULL,
            FOREIGN KEY (exercise_name) REFERENCES exercises (name)
        )
    """)
    
    cur.execute("""
        CREATE TABLE categories (
            name TEXT PRIMARY KEY,
            routine_count INTEGER NOT NULL,
            exercise_count INTEGER NOT NULL
        )
    """)
    
    # Insert categories
    for cat_name, cat_obj in categories_db.items():
        cur.execute(
            "INSERT INTO categories (name, routine_count, exercise_count) VALUES (?, ?, ?)",
            (cat_name, cat_obj["routine_count"], cat_obj["exercise_count"]),
        )
        
    # Insert routines
    for r in routines:
        cur.execute(
            """INSERT INTO routines 
               (slug, name, category, duration, description, url, thumbnail_url, exercise_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                r["slug"],
                r["name"],
                r["category"],
                r["duration"],
                r["description"],
                r["url"],
                r["thumbnail_url"],
                r["exercise_count"],
            ),
        )
        
    # Insert exercises & benefits
    for ex in exercises_db.values():
        cur.execute(
            """INSERT INTO exercises
               (name, slug, image_url, alt_text, instructions_json, tips_json, modifications_json, benefits_json, routine_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ex["name"],
                ex["slug"],
                ex["image_url"],
                ex["alt_text"],
                json.dumps(ex["instructions"], ensure_ascii=False),
                json.dumps(ex["tips"], ensure_ascii=False),
                json.dumps(ex["modifications"], ensure_ascii=False),
                json.dumps(ex["benefits"], ensure_ascii=False),
                ex["routine_count"],
            ),
        )
        for b in ex["benefits"]:
            cur.execute(
                "INSERT INTO exercise_benefits (exercise_name, benefit) VALUES (?, ?)",
                (ex["name"], b),
            )
            
    # Insert routine_exercises join
    for row in routine_exercises_data:
        cur.execute(
            """INSERT INTO routine_exercises
               (routine_slug, exercise_name, exercise_order, duration, duration_seconds)
               VALUES (?, ?, ?, ?, ?)""",
            (
                row["routine_slug"],
                row["exercise_name"],
                row["exercise_order"],
                row["duration"],
                row["duration_seconds"],
            ),
        )
            
    # Create indexes for fast queries
    cur.execute("CREATE INDEX idx_routine_category ON routines(category)")
    cur.execute("CREATE INDEX idx_re_routine ON routine_exercises(routine_slug)")
    cur.execute("CREATE INDEX idx_re_exercise ON routine_exercises(exercise_name)")
    cur.execute("CREATE INDEX idx_eb_benefit ON exercise_benefits(benefit)")
    cur.execute("CREATE INDEX idx_eb_exercise ON exercise_benefits(exercise_name)")
    
    conn.commit()
    conn.close()
    
    return exercises_db, categories_db


def main() -> None:
    """Main CLI execution flow."""
    parser = argparse.ArgumentParser(description="Scrape Bend routines and exercises into a complete database.")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Number of concurrent workers")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of routines to scrape (for testing)")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent, help="Directory to store outputs")
    parser.add_argument(
        "--from-cache",
        action="store_true",
        help="Rebuild all databases, JSON and CSV files from local routines.json without re-scraping",
    )
    args = parser.parse_args()

    print("=" * 70)
    print(" Bend.com Routine & Exercise Scraper (stangler-fast)")
    print("=" * 70)

    start_time = time.time()
    
    if args.from_cache:
        cached_routines_file = args.output_dir / "routines.json"
        if not cached_routines_file.exists():
            print(f"Error: Cached routines file not found at {cached_routines_file}", file=sys.stderr)
            sys.exit(1)
        print(f"\n[1/2] Loading cached routines from {cached_routines_file}...")
        with open(cached_routines_file, "r", encoding="utf-8") as f:
            scraped_routines = json.load(f)
        print(f"  ✓ Loaded {len(scraped_routines)} routines from cache")
        print("\n[2/2] Building databases (SQLite, JSON, CSV)...")
        exercises_db, categories_db = build_databases(scraped_routines, args.output_dir)
    else:
        session = build_http_session(args.workers)
        
        # Step 1: Discover routines
        print("\n[1/3] Discovering routines from bend.com...")
        all_routines = get_all_routine_slugs(session)
        print(f"  ✓ Discovered {len(all_routines)} routines on bend.com")
        
        if args.limit:
            all_routines = all_routines[:args.limit]
            print(f"  * Limiting to first {len(all_routines)} routines as requested")
            
        # Step 2: Scrape routines concurrently
        print(f"\n[2/3] Scraping {len(all_routines)} routine pages with {args.workers} workers...")
        scraped_routines = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_meta = {executor.submit(scrape_routine_page, session, r): r for r in all_routines}
            completed = 0
            total = len(all_routines)
            for future in concurrent.futures.as_completed(future_to_meta):
                meta = future_to_meta[future]
                try:
                    data = future.result()
                    scraped_routines.append(data)
                    completed += 1
                    if completed % 10 == 0 or completed == total:
                        pct = (completed / total) * 100
                        print(f"  [{completed:3d}/{total:3d}] ({pct:5.1f}%) Scraped: {meta['title']} ({data['exercise_count']} exercises)")
                except Exception as exc:
                    print(f"  ✗ Error scraping {meta['slug']}: {exc}", file=sys.stderr)
                    
        # Sort routines by slug for deterministic ordering
        scraped_routines.sort(key=lambda r: r["slug"])
        
        # Step 3: Build Databases
        print("\n[3/3] Building databases (SQLite, JSON, CSV)...")
        exercises_db, categories_db = build_databases(scraped_routines, args.output_dir)
    
    elapsed = time.time() - start_time
    
    # --- Sanity Validation Asserts ---
    assert len(scraped_routines) > 0, "No routines scraped"
    assert len(exercises_db) > 0, "No exercises extracted"
    assert (args.output_dir / "bend.db").exists(), "SQLite database was not created"
    assert (args.output_dir / "exercises.json").exists(), "exercises.json was not created"
    assert (args.output_dir / "routines.json").exists(), "routines.json was not created"
    assert (args.output_dir / "routine_exercises.json").exists(), "routine_exercises.json was not created"
    assert (args.output_dir / "exercise_order.json").exists(), "exercise_order.json was not created"
    assert (args.output_dir / "exercises.csv").exists(), "exercises.csv was not created"
    assert (args.output_dir / "routines.csv").exists(), "routines.csv was not created"
    assert (args.output_dir / "routine_exercises.csv").exists(), "routine_exercises.csv was not created"
    assert (args.output_dir / "exercise_order.csv").exists(), "exercise_order.csv was not created"
    assert (args.output_dir / "categories.csv").exists(), "categories.csv was not created"
    assert (args.output_dir / "exercise_benefits.csv").exists(), "exercise_benefits.csv was not created"
    
    # Check that 'Lunge' exists if hips-5 was scraped
    if any(r["slug"] == "hips-5" for r in scraped_routines):
        assert "Lunge" in exercises_db, "Lunge exercise should be present in exercises_db"
        lunge = exercises_db["Lunge"]
        assert len(lunge["instructions"]) > 0, "Lunge instructions should not be empty"
        assert len(lunge["tips"]) > 0, "Lunge tips should not be empty"
        assert len(lunge["modifications"]) > 0, "Lunge modifications should not be empty"
        assert len(lunge["benefits"]) > 0, "Lunge benefits should not be empty"
        assert "Hips" in lunge["benefits"], "Lunge benefits should include Hips"
        assert "Quadriceps" in lunge["benefits"], "Lunge benefits should include Quadriceps"
        
    # --- Summary Report ---
    print("\n" + "=" * 70)
    print(" SCRAPING & DATABASE GENERATION COMPLETED")
    print("=" * 70)
    print(f"Total Routines Scraped : {len(scraped_routines)}")
    print(f"Unique Exercises Found : {len(exercises_db)}")
    print(f"Categories Created     : {len(categories_db)}")
    print(f"Execution Time         : {elapsed:.2f}s")
    print(f"Output Directory       : {args.output_dir.resolve()}")
    print("\nGenerated Artifacts:")
    print(f"  • SQLite Database       : {args.output_dir / 'bend.db'}")
    print(f"  • Exercises JSON        : {args.output_dir / 'exercises.json'}")
    print(f"  • Routines JSON         : {args.output_dir / 'routines.json'}")
    print(f"  • Categories JSON       : {args.output_dir / 'categories.json'}")
    print(f"  • Routine Exercises JSON: {args.output_dir / 'routine_exercises.json'}")
    print(f"  • Exercise Order JSON   : {args.output_dir / 'exercise_order.json'}")
    print(f"  • Exercises CSV         : {args.output_dir / 'exercises.csv'}")
    print(f"  • Routines CSV          : {args.output_dir / 'routines.csv'}")
    print(f"  • Routine Exercises CSV : {args.output_dir / 'routine_exercises.csv'}")
    print(f"  • Exercise Order CSV    : {args.output_dir / 'exercise_order.csv'}")
    print(f"  • Categories CSV        : {args.output_dir / 'categories.csv'}")
    print(f"  • Exercise Benefits CSV : {args.output_dir / 'exercise_benefits.csv'}")
    
    print("\nCategories Breakdown:")
    for cat_name, cat_obj in sorted(categories_db.items(), key=lambda x: x[0]):
        print(f"  - {cat_name:20s}: {cat_obj['routine_count']:2d} routines, {cat_obj['exercise_count']:2d} unique exercises")

    if "Lunge" in exercises_db:
        lunge = exercises_db["Lunge"]
        print("\nExample Verification ('Lunge'):")
        print(f"  Image         : {lunge['image_url']}")
        print(f"  Benefits      : {lunge['benefits']}")
        print(f"  Instructions  : {len(lunge['instructions'])} steps")
        print(f"  Tips          : {len(lunge['tips'])} tips")
        print(f"  Modifications : {len(lunge['modifications'])} modifications")
        print(f"  In Routines   : {lunge['routine_count']} routines ({', '.join(lunge['routines'][:4])}...)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
