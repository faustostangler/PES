#!/usr/bin/env python3
"""Shared helper utilities and path configurations for Cresmo Pipeline scripts."""

import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

# --- Path Configurations ---
CRESMO_ROOT: Path = Path(__file__).parent.resolve()
DEFAULT_RAW_DIR: Path = CRESMO_ROOT / "raw"
DEFAULT_ENRICHED_DIR: Path = CRESMO_ROOT / "enriched"
DEFAULT_CRESMO_DIR: Path = CRESMO_ROOT
DEFAULT_CRESMO_WIKI_DIR: Path = CRESMO_ROOT / "wiki"
PROCESSED_CRESMO_LOG: Path = CRESMO_ROOT / "processed_cresmo.json"
DEFAULT_PLAYLIST_FILE: Path = CRESMO_ROOT / "playlist.txt"
DEFAULT_BRAIN_CSV: Path = CRESMO_ROOT / "brain.csv"
DEFAULT_COOKIES_FILE: Path = CRESMO_ROOT / ".yt_dlp_cookies.txt"

BRAIN_DIR: Path = Path(os.environ.get("ANTIGRAVITY_BRAIN_DIR", Path.home() / ".gemini" / "antigravity-ide" / "brain"))

_WORKSPACE_ROOT = CRESMO_ROOT.parent.parent
_CANDIDATE_SKILLS_DIRS = [
    _WORKSPACE_ROOT / ".agents" / "skills",
    Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills"),
    Path("/mnt/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills"),
]
SKILLS_ROOT: Path = next((p for p in _CANDIDATE_SKILLS_DIRS if p.exists()), _WORKSPACE_ROOT / ".agents" / "skills")

SKILL_EXPANDER_PATH: Path = SKILLS_ROOT / "cresmo-expander" / "SKILL.md"
SKILL_ATOMIC_PATH: Path = SKILLS_ROOT / "cresmo-atomic" / "SKILL.md"
SKILL_MOC_MANAGER_PATH: Path = SKILLS_ROOT / "cresmo-moc-manager" / "SKILL.md"

# --- Agent RPC & gRPC Defaults ---
DEFAULT_AGENTAPI_BINARY: Path = Path(os.environ.get(
    "ANTIGRAVITY_AGENTAPI_BINARY",
    Path.home() / ".gemini" / "antigravity-ide" / "bin" / "agentapi"
))
FALLBACK_TEST_CONVERSATION_ID: str = "0e69775c-ba22-4a48-ad18-ba6a318c9a04"
DEFAULT_LS_ADDRESS: str = "127.0.0.1:41667"
DEFAULT_CSRF_TOKEN: str = "ff53390d-3617-40f6-836e-6c5375ff5817"
GRPC_TEST_TIMEOUT_SECONDS: float = 1.5

# --- Formats & Protocols ---
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
VIDEO_DESCRIPTION_KEY: str = "video_description"
SENTINEL_PREFIX: str = (
    "CRITICAL CONTEXT RESET: Ignore ALL previous conversation history. "
    "This is a completely new, independent task. Do NOT reference any "
    "previously processed files or outputs. Treat this as your very "
    "first message in a fresh session.\n\n"
)

# --- Channel Classification Categories ---
POLITICS_BR_CHANNELS: frozenset[str] = frozenset({
    "ancapsu", 
})

# [VOLATILE] politics_br: Brazilian political scenario, inquiries, judiciary/STF/Congress decisions, national journalism.
POLITICS_BR_CHANNELS_ORIGINAL: frozenset[str] = frozenset({
    "ancapsu",
    "alexandre garcia",
    "ana paula henkel",
    "andré marsiglia",
    "andre marsiglia",
    "auriverde brasil",
    "band jornalismo",
    "brasil paralelo",
    "canal tragicômico",
    "canal tragicomico",
    "claudio dantas",
    "cláudio dantas",
    "cnn brasil",
    "cortes de direita",
    "deltan dallagnol",
    "estadão",
    "estadao",
    "felipe moura brasil",
    "fernão lara mesquita",
    "fernao lara mesquita",
    "folha de s.paulo",
    "folha de s. paulo",
    "folha de sao paulo",
    "gazeta do povo",
    "ideias radicais",
    "josé nêumanne pinto",
    "jose neumanne pinto",
    "leandro ruschel",
    "luís ernesto lacombe",
    "luis ernesto lacombe",
    "metrópoles",
    "metropoles",
    "na direita cortes",
    "nando moura",
    "o povo",
    "oiluiz tv",
    "paulo figueiredo show",
    "renato battista",
    "revista oeste",
    "rádio cbn",
    "radio cbn",
    "sbt news",
    "tv band rio",
    "veja+",
    "visão libertária",
    "visao libertaria",
    "paulo baltokoski",
    "jeffrey chiquini",
    "spotniks",
})

# [VOLATILE] geopolitics: Foreign affairs, international armed conflicts, superpower strategy, diplomacy.
GEOPOLITICS_CHANNELS: frozenset[str] = frozenset({
    "behind asia",
    "china uncensored",
    "china unscripted",
    "heni ozi cukier",
    "hoje no mundo militar",
    "knowledgia",
    "makarov",
    "professor ricardo marcílio",
    "professor ricardo marcilio",
    "serpentza",
    "spectacles",
    "world revolving",
})

# [PERENNIAL] tech_ai: Artificial Intelligence, LLMs, software engineering, cloud, DevOps, developer ecosystem.
TECH_AI_CHANNELS: frozenset[str] = frozenset({
    "ag grid",
    "ai engineer",
    "ai progbr",
    "ai search",
    "anderson adelino | ia e automações",
    "anderson adelino | ia e automacoes",
    "andrej karpathy",
    "augusto galego",
    "austin marchese",
    "ben ai",
    "boot dev",
    "brain station",
    "chrome for developers",
    "cloud codes",
    "cododev",
    "cole medin",
    "cyberflow",
    "código fonte tv",
    "codigo fonte tv",
    "dataquest",
    "dev aprender | jhonatan de souza",
    "devops toolbox",
    "eli rigobeli - ai",
    "estudio 68 by micah 6 ai",
    "estúdio 68 by micah 6 ai",
    "fabio akita",
    "fábio akita",
    "filipe deschamps",
    "fireship",
    "freecodecamp.org",
    "freecodecamp",
    "google deepmind",
    "google for developers",
    "ibm technology",
    "italo diego teotonio",
    "ítalo diego teotônio",
    "jeff geerling",
    "josé ángel ai",
    "jose angel ai",
    "julian goldie seo",
    "lucas montano",
    "maestros da ia",
    "mano deyvin",
    "marie haynes",
    "matheus battisti - hora de codar",
    "matheus battisti – hora de codar",
    "mindmesh ai",
    "mischa van den burg",
    "nate friedman",
    "nate herk | ai automation",
    "networkchuck",
    "neurix",
    "onde eu clico",
    "privacy matters",
    "riley brown",
    "rob braxman tech",
    "safesrc",
    "sandeco channel - decomplicated ia",
    "sandeep swadia",
    "systemdr - scalable system design",
    "systemdr – scalable system design",
    "tech with tim",
    "tool drop",
    "two minute papers",
    "vini - ai coders academy",
    "vini – ai coders academy",
    "well pires",
    "worldofai",
    "xperiun | data analytics",
    "yurirdev",
    "inteligência mil grau",
    "inteligencia mil grau",
    "sancler miranda",
    "ronnald hawk",
    "elton machado",
    "jeff su",
    "paul j lipsky",
    "ana jords",
})

# [PERENNIAL] finance: Financial markets, macroeconomics, Austrian economics, valuation, personal finance.
FINANCE_CHANNELS: frozenset[str] = frozenset({
    "andrei jikh",
    "breno perrucho - jovens de negócios",
    "breno perrucho – jovens de negócios",
    "breno perrucho - jovens de negocios",
    "brian feroldi",
    "bruno perini - você mais rico",
    "bruno perini – você mais rico",
    "bruno perini - voce mais rico",
    "capital global",
    "clube do valor",
    "curioso mercado",
    "dinheiro com você - por william ribeiro",
    "dinheiro com você – por william ribeiro",
    "dinheiro com voce - por william ribeiro",
    "dividendos news",
    "eo",
    "exame",
    "fernando ulrich",
    "helio beltrão",
    "hélio beltrão",
    "helio beltrao",
    "instituto mises brasil",
    "investidor sardinha l raul sena",
    "investidor sardinha | raul sena",
    "investidor sardinha",
    "market makers",
    "o conselho | flávio augusto",
    "o conselho | flavio augusto",
    "o primo rico",
    "rafael quintanilha – quantbrasil",
    "rafael quintanilha - quantbrasil",
    "rafael quintanilha",
    "renato augusto",
    "tapa da mão invisível",
    "tapa da mao invisivel",
    "conhecimento disruptivo",
    "adam erhart",
    "bruno okamoto",
    "bruno ávila",
    "bruno avila",
})

# [PERENNIAL] engineering: Pure and applied math, physics, astrophysics, civil/mech/electrical engineering, science.
ENGINEERING_CHANNELS: frozenset[str] = frozenset({
    "3blue1brown",
    "anton petrov",
    "braintruffle",
    "ciência todo dia",
    "ciencia todo dia",
    "engenheiro matheus",
    "floatheadphysics",
    "hank green",
    "hindemburg melao jr.",
    "hindemburg melão jr.",
    "infinitamente",
    "kurzgesagt – in a nutshell",
    "kurzgesagt - in a nutshell",
    "matematizei",
    "practical engineering",
    "real science",
    "scienceclic english",
    "simulation sandbox",
    "somos míopes porque somos breves",
    "somos miopes porque somos breves",
    "steve mould",
    "technology connections",
    "veritasium",
    "ponto em comum",
})

# [PERENNIAL] architecture: Architectural projects, interiors, sustainable construction, biomimicry, housing comparison.
ARCHITECTURE_CHANNELS: frozenset[str] = frozenset({
    "laion fernandes - arquitetura e interiores",
    "laion fernandes – arquitetura e interiores",
    "planarq campos",
    "ricardo molina usa",
    "ugreen consultoria e educação",
    "ugreen consultoria e educacao",
    "ugreen: decifrando a ciência das construções",
    "ugreen: decifrando a ciencia das construcoes",
})

# [PERENNIAL] history: Ancient and modern history, archaeology, etymology, language evolution, historical docs.
HISTORY_CHANNELS: frozenset[str] = frozenset({
    "estranha história",
    "estranha historia",
    "etimosofia",
    "história simples",
    "historia simples",
    "jaydone history",
    "marcelo andrade",
    "periscopefilm",
    "robwords",
    "study of antiquity and the middle ages",
    "the present past",
    "words unravelled",
})

# [PERENNIAL] philosophy: Classical and modern philosophy, analytical psychology, communication, negotiation, rhetoric.
PHILOSOPHY_CHANNELS: frozenset[str] = frozenset({
    "a odisseia interior",
    "a psique",
    "big think",
    "clóvis de barros",
    "clovis de barros",
    "design theory",
    "jefferson fisher",
    "lara brenner",
    "marcos campos",
    "metaforando",
    "paulo cruz",
    "sprouts",
    "descobri depois de adulta",
    "descobri depois de adulta podcast",
    "ted-ed",
})

# [PERENNIAL] health: Preventive medicine, nutrition, metabolism, mental models, physical health, self-mastery.
HEALTH_CHANNELS: frozenset[str] = frozenset({
    "dr. bruno salles, phd | psicólogo & neurocientista",
    "dr. bruno salles, phd | psicologo & neurocientista",
    "chris voss & the black swan group",
    "el professor da oratória",
    "el professor da oratoria",
    "ernesto reis",
    "rationality rules",
    "arata academy",
    "artem kirsanov",
    "dr. eric berg dc",
    "sajjaad khader",
    "sleepwise",
    "smarter while you sleep",
})

# [VOLATILE] entertainment: Cinema, series, TV backstage, television history, pop culture.
ENTERTAINMENT_CHANNELS: frozenset[str] = frozenset({
    "canal 90",
    "canal peewee",
    "nerd show",
    "ricardo feltrin",
})

# [VOLATILE] uncategorized: Fallback for all other unclassified / atypical channels.
DEFAULT_CHANNEL_DOMAIN: str = "uncategorized"
DEFAULT_CHANNEL_CATEGORY: str = "volatile"
DEFAULT_CATEGORIES: tuple[str, ...] = ("politics_br",)

# --- Compiled Regexes ---
TRANSCRIPTION_SPLIT_REGEX: re.Pattern[str] = re.compile(r"^---$", flags=re.MULTILINE)
PID_REGEX: re.Pattern[str] = re.compile(r"^\S+\s+(\d+)")
TOKEN_REGEX: re.Pattern[str] = re.compile(r"--csrf_token\s+([a-f0-9\-]+)")
PORT_REGEX: re.Pattern[str] = re.compile(r"127\.0\.0\.1:(\d+)")

# Detects Antigravity baseline quota messages, e.g.:
# "Your plan's baseline quota will refresh on 8/21/2026, 7:31:36 AM."
QUOTA_REFRESH_PATTERN: re.Pattern[str] = re.compile(
    r"Your plan's baseline quota will refresh on\s+(\d{1,2}/\d{1,2}/\d{4}),?\s+(\d{1,2}:\d{2}:\d{2}\s+[AP]M)",
    re.IGNORECASE,
)


# --- Quota Detection Helpers ---

def parse_quota_refresh_time(text: str) -> datetime.datetime | None:
    """Extract the quota refresh datetime from an Antigravity API rate-limit message.

    Parses strings of the form:
        'Your plan's baseline quota will refresh on M/D/YYYY, H:MM:SS AM/PM.'

    Args:
        text: Raw string that may contain an Antigravity quota exhaustion message.

    Returns:
        Parsed datetime.datetime for the refresh deadline, or None if not found.
    """
    match = QUOTA_REFRESH_PATTERN.search(text)
    if not match:
        return None
    try:
        return datetime.datetime.strptime(
            f"{match.group(1)} {match.group(2)}", "%m/%d/%Y %I:%M:%S %p"
        )
    except ValueError:
        return None


def scan_session_for_quota_refresh(
    session_id: str, brain_dir: Path | None = None
) -> datetime.datetime | None:
    """Scan the active session transcript for a baseline quota refresh message.

    Reads the session's transcript.jsonl in reverse to find the most recent
    Antigravity API quota exhaustion message. Only returns a deadline that is
    still in the future (i.e., the quota has not yet refreshed).

    Args:
        session_id: Target Antigravity conversation identifier.
        brain_dir: Optional custom path to brain root directory (defaults to BRAIN_DIR).

    Returns:
        datetime.datetime of the upcoming quota refresh, or None if not detected.
    """
    target_brain_dir = brain_dir if brain_dir is not None else BRAIN_DIR
    log_path = (
        target_brain_dir / session_id / ".system_generated" / "logs" / "transcript.jsonl"
    )
    if not log_path.exists():
        return None
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Scan only the last 200 entries for performance; quota messages are always recent
        for line in reversed(lines[-200:]):
            try:
                entry = json.loads(line.strip())
                content = str(entry.get("content") or "")
                parsed = parse_quota_refresh_time(content)
                if parsed and parsed > datetime.datetime.now():
                    return parsed
            except Exception:
                continue
    except Exception:
        pass
    return None


# --- File & Data Helpers ---

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

        parts = TRANSCRIPTION_SPLIT_REGEX.split(content)

        i = 1
        while i < len(parts):
            yaml_text = parts[i]
            text_content = parts[i + 1].strip() if i + 1 < len(parts) else ""

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
                if key == VIDEO_DESCRIPTION_KEY:
                    in_desc = True
                    continue
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                meta[key] = val

            if desc_lines:
                meta[VIDEO_DESCRIPTION_KEY] = "\n".join(desc_lines)

            metadata_list.append({
                "metadata": meta,
                "text": text_content,
            })
            i += 2
    except Exception as e:
        print(f"Error parsing merged transcriptions in {file_path.name}: {e}")
    return metadata_list


# --- Idempotency & Log Management ---

def load_processed_cresmo_log(log_path: Path = PROCESSED_CRESMO_LOG) -> set[str]:
    """Load set of completed video_ids from processed_cresmo.json log."""
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    return set(data.keys())
        except Exception as e:
            print(f"[Log Warning] Failed to read {log_path.name}: {e}")
    return set()


def save_processed_cresmo_log(
    video_id: str,
    metadata: dict | None = None,
    log_path: Path = PROCESSED_CRESMO_LOG,
) -> None:
    """Save processed video_id entry to processed_cresmo.json."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    records = {}
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                if isinstance(raw_data, dict):
                    records = raw_data
                elif isinstance(raw_data, list):
                    records = {vid: {"processed_at": time.strftime(DATETIME_FORMAT)} for vid in raw_data}
        except Exception:
            records = {}

    records[video_id] = {
        "processed_at": time.strftime(DATETIME_FORMAT),
        "channel_name": metadata.get("channel_name", "") if metadata else "",
        "video_title": metadata.get("video_title", "") if metadata else "",
    }

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


# --- Channel Classification ---

def classify_channel(channel_name: str) -> tuple[str, str]:
    """Classifies source channel deterministically into (domain, category_type)."""
    name_clean = channel_name.lower().strip()

    if name_clean in POLITICS_BR_CHANNELS:
        return "politics_br", "volatile"
    elif name_clean in GEOPOLITICS_CHANNELS:
        return "geopolitics", "volatile"
    elif name_clean in TECH_AI_CHANNELS:
        return "tech_ai", "perennial"
    elif name_clean in FINANCE_CHANNELS:
        return "finance", "perennial"
    elif name_clean in ENGINEERING_CHANNELS:
        return "engineering", "perennial"
    elif name_clean in ARCHITECTURE_CHANNELS:
        return "architecture", "perennial"
    elif name_clean in HISTORY_CHANNELS:
        return "history", "perennial"
    elif name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    elif name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    elif name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


# --- Agent RPC & Session Management ---

def get_agentapi_binary() -> str:
    """Locate agentapi executable binary."""
    return str(DEFAULT_AGENTAPI_BINARY) if DEFAULT_AGENTAPI_BINARY.exists() else "agentapi"


def get_antigravity_env() -> dict[str, str]:
    """Resolve and validate active IDE gRPC environment credentials."""
    env = os.environ.copy()
    binary_path = get_agentapi_binary()

    ls_addr = env.get("ANTIGRAVITY_LS_ADDRESS")
    csrf_token = env.get("ANTIGRAVITY_CSRF_TOKEN")

    def is_valid_grpc(port: str, token: str) -> bool:
        test_env = env.copy()
        test_env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
        test_env["ANTIGRAVITY_CSRF_TOKEN"] = token
        try:
            res = subprocess.run(
                [binary_path, "get-conversation-metadata", FALLBACK_TEST_CONVERSATION_ID],
                capture_output=True,
                text=True,
                timeout=GRPC_TEST_TIMEOUT_SECONDS,
                env=test_env,
            )
            out = (res.stdout + "\n" + res.stderr).lower()
            return (
                res.returncode == 0
                and "error reading server preface" not in out
                and "connection reset" not in out
                and "connection refused" not in out
                and "unavailable" not in out
            )
        except Exception:
            return False

    if ls_addr and ":" in ls_addr:
        port = ls_addr.split(":", 1)[1]
        if is_valid_grpc(port, csrf_token or ""):
            return env

    try:
        ps_res = subprocess.run(["ps", "aux"], capture_output=True, text=True, check=False)
        for line in ps_res.stdout.splitlines():
            if "language_server" in line and "--csrf_token" in line:
                pid_m = PID_REGEX.search(line)
                token_m = TOKEN_REGEX.search(line)
                if pid_m and token_m:
                    pid = pid_m.group(1)
                    token = token_m.group(1)
                    ss_res = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True, check=False)
                    for ss_line in ss_res.stdout.splitlines():
                        if f"pid={pid}," in ss_line:
                            port_m = PORT_REGEX.search(ss_line)
                            if port_m:
                                port = port_m.group(1)
                                if is_valid_grpc(port, token):
                                    env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
                                    env["ANTIGRAVITY_CSRF_TOKEN"] = token
                                    return env
    except Exception as e:
        print(f"[Env Warning] LS scan: {e}")

    env["ANTIGRAVITY_LS_ADDRESS"] = DEFAULT_LS_ADDRESS
    env["ANTIGRAVITY_CSRF_TOKEN"] = DEFAULT_CSRF_TOKEN
    return env


def resolve_active_session() -> str:
    """Resolve active session ID, auto-detect from brain logs, or allocate a NEW session."""
    env_id = os.getenv("ANTIGRAVITY_CONVERSATION_ID") or os.getenv("ANTIGRAVITY_TRAJECTORY_ID")
    if env_id:
        return env_id

    if BRAIN_DIR.exists():
        recent_logs = sorted(
            BRAIN_DIR.glob("*/.system_generated/logs/transcript.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if recent_logs:
            return recent_logs[0].parent.parent.parent.name

    binary_path = get_agentapi_binary()
    env = get_antigravity_env()
    res = subprocess.run([binary_path, "new-conversation"], capture_output=True, text=True, env=env)
    try:
        data = json.loads(res.stdout)
        new_id = data.get("response", {}).get("conversationId") or data.get("conversationId")
        if new_id:
            return new_id
    except Exception:
        pass

    raise RuntimeError("Failed to resolve or allocate active Antigravity session ID.")


def send_agent_message(prompt: str, session_id: str) -> str:
    """Dispatch RPC payload to target agent session."""
    binary_path = get_agentapi_binary()
    env = get_antigravity_env()
    cmd = [binary_path, "send-message", session_id, prompt]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return res.stdout.strip()


def clear_session_history(session_id: str, restart_server: bool = False, brain_dir: Path | None = None) -> bool:
    """Purge active agent session history (transcript.jsonl and message files) to isolate context.

    Args:
        session_id: Target agent conversation identifier.
        restart_server: If True, terminates the active Language Server process to force fresh context reload.
        brain_dir: Optional custom path to brain root directory (defaults to BRAIN_DIR).

    Returns:
        bool: True if session directory was located and purged, False otherwise.
    """
    target_brain_dir = brain_dir if brain_dir is not None else BRAIN_DIR
    session_dir = target_brain_dir / session_id
    if not session_dir.exists():
        return False

    purged = False
    # 1. Truncate transcript logs
    for log_filename in ("transcript.jsonl", "transcript_full.jsonl"):
        jsonl_path = session_dir / ".system_generated" / "logs" / log_filename
        if jsonl_path.exists():
            try:
                jsonl_path.write_text("", encoding="utf-8")
                purged = True
            except Exception as e:
                print(f"[Context Purge Warning] Failed to truncate {jsonl_path.name}: {e}")

    # 2. Delete message files
    messages_dir = session_dir / ".system_generated" / "messages"
    if messages_dir.exists():
        for msg_file in messages_dir.glob("*.json"):
            try:
                msg_file.unlink(missing_ok=True)
                purged = True
            except Exception:
                pass

    return purged or session_dir.exists()
