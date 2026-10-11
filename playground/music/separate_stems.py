#!/usr/bin/env python3
"""Demucs Stem Extraction (Meta AI) with Ollama AI Tagging and YouTube Playlist Downloader (yt-dlp).

Supports single YouTube videos and full YouTube/YouTube Music playlists.
Default mode: 6 Stems (Vocals, Drums, Bass, Other, Guitar, Piano) with MAXIMUM quality.
Downloads and organizes audio and stems in the same folder as:
  {gênero}/{artista} - {música}.mp3
  {gênero}/{artista} - {música} - vocals.mp3
  {gênero}/{artista} - {música} - drums.mp3
  {gênero}/{artista} - {música} - bass.mp3
  {gênero}/{artista} - {música} - other.mp3
  {gênero}/{artista} - {música} - guitar.mp3
  {gênero}/{artista} - {música} - piano.mp3
"""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any, cast
import urllib.request
import torch
import yt_dlp
from demucs.separate import main as demucs_main

# ==============================================================================
# CONFIGURAÇÃO DE QUALIDADE (DEMUCS / META AI)
# ==============================================================================
# O Demucs possui 4 dimensões principais de ajuste de fidelidade vs performance:
#
# 1. MODELO PRE-TREINADO (-n / --name):
#    - PADRÃO (6 STEMS): "htdemucs_6s" (6 stems: Vocals, Drums, Bass, Other, Guitar, Piano)
#    - 4 STEMS MAX:      "htdemucs_ft" (Ensemble fine-tuned para 4 stems)
#    - BALANCED:         "htdemucs"    (Modelo base padrão de 4 stems)
#    - FAST / LOW:       "mdx_extra_q" (Quantizado / rápido para testes)
#
# 2. SHIFTS (--shifts): Truque de estabilização equivariante (random time/phase shifts).
#    Executa a rede N vezes com pequenos deslocamentos no tempo e calcula a média.
#    Elimina artefatos metálicos e ruídos de fase.
#    - MAX:        5 (ou 10 conforme o paper original da Meta para pureza máxima de estúdio)
#    - BALANCED:   1 ou 2
#    - FAST / LOW: 0 (desligado, 1 única passada direta)
#
# 3. OVERLAP (--overlap): Sobreposição entre as janelas de processamento de áudio (chunks).
#    - MAX:        0.50 (50% de sobreposição com cross-fade contínuo, elimina costuras entre blocos)
#    - BALANCED:   0.25 (padrão Demucs)
#    - FAST / LOW: 0.10 (mínimo, rápido)
#
# 4. MP3 BITRATE & PRESET (--mp3-bitrate / --mp3-preset):
#    - MAX:        320 kbps (bitrate máximo do formato MP3) com preset 2 (máxima qualidade do codificador LAME)
#    - BALANCED:   256 kbps (preset 4)
#    - FAST / LOW: 192 ou 128 kbps (preset 7)
# ==============================================================================

# --- Defaults configurados no MÁXIMO absoluto com 6 STEMS ---
DEFAULT_MODEL = "htdemucs_6s"    # Modelo de 6 Stems (Vocals, Drums, Bass, Other, Guitar, Piano)
DEFAULT_SHIFTS = 5               # 5 passagens de estabilização equivariante (elimina artefatos)
DEFAULT_OVERLAP = 0.50           # 50% de sobreposição para junção perfeita dos chunks
DEFAULT_MP3_BITRATE = 320        # 320 kbps (qualidade máxima de MP3)
DEFAULT_MP3_PRESET = 2           # Preset 2 do encoder LAME (máxima fidelidade acústica)
DEFAULT_CLIP_MODE = "rescale"    # Evita qualquer distorção digital reescalando picos > 0dBFS

# Lista canônica dos 6 stems esperados
STEMS_6S = ["vocals", "drums", "bass", "other", "guitar", "piano"]
STEMS_4S = ["vocals", "drums", "bass", "other"]

DEFAULT_PLAYLIST_FILE = Path(__file__).parent / "playlist.txt"
DEFAULT_LIBRARY_DIR = Path(__file__).parent / "library"
DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:latest"


def sanitize_filename(name: str) -> str:
    """Remove or replace characters that are invalid in file and folder paths."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned or "Unknown"


def query_ollama_metadata(
    title: str,
    channel: str,
    description: str,
    model: str = DEFAULT_OLLAMA_MODEL,
    host: str = OLLAMA_HOST,
) -> dict[str, str]:
    """Classify genre, artist, and track name using local Ollama model."""
    prompt = f"""Given the music video title, channel, and description, identify:
1. genre (broad musical genre like "Rock", "Samba-Reggae", "Pop", "Jazz", "Hip Hop", "Eletronica", "MPB", "Reggae", etc. - clean and suitable for folder naming)
2. artist (main artist or band name)
3. track (song title, without feat or extra noise)

Input:
Title: {title}
Channel/Uploader: {channel}
Description:
{description[:1500]}

Respond strictly in valid JSON with keys "genre", "artist", "track". Do not include markdown codeblocks or explanation.
"""
    for attempt in range(2):
        try:
            req = urllib.request.Request(
                f"{host}/api/generate",
                data=json.dumps({
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw_res = json.loads(resp.read().decode("utf-8"))
                data = json.loads(raw_res.get("response", "{}"))
                genre = sanitize_filename(data.get("genre") or "Unknown")
                artist = sanitize_filename(data.get("artist") or channel or "Unknown")
                track = sanitize_filename(data.get("track") or title or "Track")
                return {"genre": genre, "artist": artist, "track": track}
        except Exception as e:
            if attempt == 0:
                print(f"[Ollama] Notice: Attempt 1 failed ({e}). Retrying...")
                continue
            print(f"[Ollama] Warning: Could not infer metadata via LLM ({e}). Using raw tags.")
            break

    return {
        "genre": "Unknown",
        "artist": sanitize_filename(channel or "Unknown"),
        "track": sanitize_filename(title or "Track"),
    }


def stems_already_exist(audio_path: Path, stems: list[str] = STEMS_6S) -> bool:
    """Check if all stem MP3 files already exist in the target folder."""
    target_dir = audio_path.parent
    base_stem_name = audio_path.stem
    return all((target_dir / f"{base_stem_name} - {s}.mp3").exists() for s in stems)


def extract_tracks_from_url(url: str) -> list[Any]:
    """Extract all video track entries from a single URL or YouTube playlist."""
    ydl_opts: dict[str, Any] = {
        "quiet": True,
        "extract_flat": "in_playlist",
        "noplaylist": False,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"[yt-dlp] Error extracting URL {url}: {e}")
            return []

        if not info:
            return []

        entries = info.get("entries")
        if entries is not None:
            entry_list = [e for e in entries if e]
            print(f"[yt-dlp] Playlist detected: '{info.get('title', 'Untitled')}' with {len(entry_list)} tracks.")
            return list(entry_list)
        else:
            return [info]


def download_single_track(
    entry: dict[str, Any] | Any,
    library_dir: Path,
    expected_stems: list[str] = STEMS_6S,
    ollama_model: str = DEFAULT_OLLAMA_MODEL,
) -> tuple[Path, dict[str, str], bool]:
    """Tag with Ollama, download audio if needed, returning (mp3_path, metadata, already_had_stems)."""
    title = entry.get("title") or "Unknown Title"
    channel = entry.get("uploader") or entry.get("channel") or "Unknown Artist"
    description = entry.get("description") or ""

    video_url_candidate: str | None = entry.get("webpage_url") or entry.get("url")
    if not video_url_candidate and entry.get("id"):
        video_url_candidate = f"https://music.youtube.com/watch?v={entry.get('id')}"

    video_url: str = video_url_candidate or ""

    if not description and video_url:
        try:
            probe_opts: dict[str, Any] = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(cast(Any, probe_opts)) as ydl:
                full_info = ydl.extract_info(video_url, download=False)
                if full_info:
                    title = full_info.get("title") or title
                    channel = full_info.get("uploader") or full_info.get("channel") or channel
                    description = full_info.get("description") or ""
        except Exception:
            pass

    print(f"\n[AI Tagging] Asking Ollama ({ollama_model}) for metadata: '{title}'...")
    metadata = query_ollama_metadata(
        title=title,
        channel=channel,
        description=description,
        model=ollama_model,
    )
    genre = metadata["genre"]
    artist = metadata["artist"]
    track = metadata["track"]

    print(f"[AI Tagging] Identified -> Gênero: '{genre}' | Artista: '{artist}' | Música: '{track}'")

    file_stem = f"{artist} - {track}"
    
    # Check if track is already present in ANY genre subfolder in library
    existing_in_library = list(library_dir.glob(f"*/{file_stem}.mp3"))
    if existing_in_library:
        expected_mp3 = existing_in_library[0]
        genre_dir = expected_mp3.parent
        print(f"[Library] Found existing audio in: {genre_dir.name}/{expected_mp3.name}")
    else:
        genre_dir = library_dir / genre
        genre_dir.mkdir(parents=True, exist_ok=True)
        expected_mp3 = genre_dir / f"{file_stem}.mp3"

    # Check if all expected stems (default: 6 stems) already exist
    if stems_already_exist(expected_mp3, stems=expected_stems):
        print(f"[Cache] All {len(expected_stems)} stems already exist for: '{file_stem}'. Skipping.")
        return expected_mp3, metadata, True

    if expected_mp3.exists():
        print(f"[Library] Audio already downloaded: {expected_mp3.name}")
        return expected_mp3, metadata, False

    out_template = str(genre_dir / f"{file_stem}.%(ext)s")
    ydl_dl_opts: dict[str, Any] = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "quiet": False,
        "no_warnings": True,
    }

    if not video_url:
        raise ValueError(f"Could not determine video URL for entry: {title}")

    print(f"[yt-dlp] Downloading audio: {title} -> {file_stem}.mp3")
    with yt_dlp.YoutubeDL(cast(Any, ydl_dl_opts)) as ydl:
        ydl.download([video_url])

    assert expected_mp3.exists(), f"Downloaded audio not found at: {expected_mp3}"
    print(f"[yt-dlp] Saved: {expected_mp3.name}")
    return expected_mp3, metadata, False


def separate_stems_in_place(
    audio_path: Path,
    model: str = DEFAULT_MODEL,
    device: str = DEFAULT_DEVICE,
    shifts: int = DEFAULT_SHIFTS,
    overlap: float = DEFAULT_OVERLAP,
    mp3_bitrate: int = DEFAULT_MP3_BITRATE,
    mp3_preset: int = DEFAULT_MP3_PRESET,
    clip_mode: str = DEFAULT_CLIP_MODE,
    two_stems: str | None = None,
) -> list[Path]:
    """Separate audio into stems saved in the same directory as {artist} - {musica} - {stem}.mp3."""
    audio_path = Path(audio_path).resolve()
    assert audio_path.exists(), f"Input audio file not found: {audio_path}"

    target_dir = audio_path.parent
    base_stem_name = audio_path.stem

    temp_demucs_dir = target_dir / ".tmp_demucs"
    temp_demucs_dir.mkdir(parents=True, exist_ok=True)

    cmd_args = [
        "-n", model,
        "-o", str(temp_demucs_dir),
        "-d", device,
        "--shifts", str(shifts),
        "--overlap", str(overlap),
        "--mp3",
        "--mp3-bitrate", str(mp3_bitrate),
        "--mp3-preset", str(mp3_preset),
        "--clip-mode", clip_mode,
    ]

    if two_stems:
        cmd_args.extend(["--two-stems", two_stems])

    cmd_args.append(str(audio_path))

    print(f"\n[Demucs] Separating stems for: {audio_path.name}")
    print(f"[Demucs] Config: Model={model} | Shifts={shifts} | Overlap={overlap*100:.0f}% | MP3={mp3_bitrate}kbps | Device={device}")
    demucs_main(cmd_args)

    raw_output_folder = temp_demucs_dir / model / audio_path.stem
    generated_stems: list[Path] = []

    if raw_output_folder.exists():
        for stem_file in raw_output_folder.glob("*.mp3"):
            stem_type = stem_file.stem
            final_stem_path = target_dir / f"{base_stem_name} - {stem_type}.mp3"
            shutil.move(str(stem_file), str(final_stem_path))
            generated_stems.append(final_stem_path)

        shutil.rmtree(temp_demucs_dir, ignore_errors=True)

    return generated_stems


def read_playlist_file(playlist_path: Path) -> list[str]:
    """Read URLs from a text file, ignoring comments and blank lines."""
    if not playlist_path.exists():
        return []
    with open(playlist_path, encoding="utf-8") as f:
        lines = [line.strip() for line in f]
    return [line for line in lines if line and not line.startswith("#")]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download YouTube videos or playlists and save stems as {artista} - {musica} - {stem}.mp3 in the same {genre}/ folder (Default: 6 Stems MAX)."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="YouTube URL, playlist URL, local audio file, or text file with links (default: playlist.txt)",
    )
    parser.add_argument("-o", "--out", default=DEFAULT_LIBRARY_DIR, type=Path, help="Root directory for the music library")
    
    # Presets de qualidade
    parser.add_argument(
        "--preset",
        choices=["max", "balanced", "fast"],
        default="max",
        help="Quality preset: 'max' (htdemucs_6s, 5 shifts, 50%% overlap, 320kbps), 'balanced' (htdemucs_6s, 1 shift, 25%% overlap), 'fast' (htdemucs_6s, 0 shifts, 10%% overlap)",
    )
    parser.add_argument("-m", "--model", default=None, help=f"Override Demucs model name (default: {DEFAULT_MODEL} [6 stems])")
    parser.add_argument("--shifts", type=int, default=None, help="Override equivariant stabilization shifts (0-10)")
    parser.add_argument("--overlap", type=float, default=None, help="Override chunk overlap fraction (0.1 - 0.75)")
    parser.add_argument("-d", "--device", default=DEFAULT_DEVICE, help=f"Execution device (default: {DEFAULT_DEVICE})")
    parser.add_argument("--two-stems", default=None, help="Isolate one stem (e.g., 'vocals') and rest into instrumental")
    parser.add_argument("--ollama-model", default=DEFAULT_OLLAMA_MODEL, help=f"Ollama model for tagging (default: {DEFAULT_OLLAMA_MODEL})")

    args = parser.parse_args()

    # Aplicação de Presets (padrão absoluto: htdemucs_6s)
    default_active_model = args.model or DEFAULT_MODEL
    if args.preset == "max":
        model = default_active_model
        shifts = args.shifts if args.shifts is not None else 5
        overlap = args.overlap if args.overlap is not None else 0.50
        mp3_bitrate = 320
    elif args.preset == "balanced":
        model = default_active_model
        shifts = args.shifts if args.shifts is not None else 1
        overlap = args.overlap if args.overlap is not None else 0.25
        mp3_bitrate = 256
    else:  # fast
        model = default_active_model
        shifts = args.shifts if args.shifts is not None else 0
        overlap = args.overlap if args.overlap is not None else 0.10
        mp3_bitrate = 192

    expected_stems = STEMS_6S if "6s" in model else STEMS_4S

    urls_or_files: list[str] = []
    if args.target:
        target_path = Path(args.target)
        if target_path.exists() and target_path.is_file() and target_path.suffix == ".txt":
            urls_or_files = read_playlist_file(target_path)
        else:
            urls_or_files = [args.target]
    elif DEFAULT_PLAYLIST_FILE.exists():
        urls_or_files = read_playlist_file(DEFAULT_PLAYLIST_FILE)

    if not urls_or_files:
        print("Demucs 6-Stems & Ollama Music Library Extractor")
        print(f"Device: {DEFAULT_DEVICE} (CUDA: {torch.cuda.is_available()}) | Ollama: {args.ollama_model}")
        print(f"Default Preset: MAX (Model: {model} [6 STEMS], Shifts: {shifts}, Overlap: {overlap*100:.0f}%, Bitrate: {mp3_bitrate}k)")
        print(f"\nNo target specified and {DEFAULT_PLAYLIST_FILE.name} is empty.")
        print("\nHow to use:")
        print("  1. Add YouTube URLs or Playlists to playground/music/playlist.txt and run:")
        print("     python playground/music/separate_stems.py")
        sys.exit(0)

    print(f"Found {len(urls_or_files)} line(s) in playlist/input.")
    print(f"Active Quality Preset: {args.preset.upper()} (Model={model} [6 STEMS], Shifts={shifts}, Overlap={overlap*100:.0f}%, MP3={mp3_bitrate}kbps)")

    for line_idx, raw_item in enumerate(urls_or_files, start=1):
        print(f"\n==================================================")
        print(f"[{line_idx}/{len(urls_or_files)}] Reading: {raw_item}")
        print(f"==================================================")

        if raw_item.startswith("http://") or raw_item.startswith("https://"):
            track_entries = extract_tracks_from_url(raw_item)
            if not track_entries:
                print(f"[Warning] No valid tracks extracted from: {raw_item}")
                continue

            print(f"Total track(s) to process for this URL: {len(track_entries)}")
            for t_idx, entry in enumerate(track_entries, start=1):
                print(f"\n--- Processing Track [{t_idx}/{len(track_entries)}] ---")
                audio_file, meta, had_stems = download_single_track(
                    entry=entry,
                    library_dir=args.out,
                    expected_stems=expected_stems,
                    ollama_model=args.ollama_model,
                )

                if had_stems:
                    continue

                stems = separate_stems_in_place(
                    audio_path=audio_file,
                    model=model,
                    device=args.device,
                    shifts=shifts,
                    overlap=overlap,
                    mp3_bitrate=mp3_bitrate,
                    mp3_preset=DEFAULT_MP3_PRESET,
                    clip_mode=DEFAULT_CLIP_MODE,
                    two_stems=args.two_stems,
                )

                print(f"\n✓ Stems saved in same folder: {audio_file.parent}")
                for stem_file in sorted(stems):
                    size_mb = stem_file.stat().st_size / (1024 * 1024)
                    print(f"  • {stem_file.name} ({size_mb:.2f} MB)")

        else:
            local_path = Path(raw_item)
            assert local_path.exists(), f"Local audio file not found: {local_path}"
            if stems_already_exist(local_path, stems=expected_stems):
                print(f"[Cache] All {len(expected_stems)} stems already exist for: '{local_path.name}'. Skipping.")
                continue

            stems = separate_stems_in_place(
                audio_path=local_path,
                model=model,
                device=args.device,
                shifts=shifts,
                overlap=overlap,
                mp3_bitrate=mp3_bitrate,
                mp3_preset=DEFAULT_MP3_PRESET,
                clip_mode=DEFAULT_CLIP_MODE,
                two_stems=args.two_stems,
            )
            print(f"\n✓ Stems saved in same folder: {local_path.parent}")
            for stem_file in sorted(stems):
                size_mb = stem_file.stat().st_size / (1024 * 1024)
                print(f"  • {stem_file.name} ({size_mb:.2f} MB)")

    print("\n✓ All items processed and organized successfully!")
