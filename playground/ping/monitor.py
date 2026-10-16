import csv
import json
import os
import sqlite3
import subprocess
import threading
import time
import urllib.request
from datetime import datetime, timedelta
from typing import Any

from icmplib import ping as icmp_ping
import speedtest

TARGET_IP = os.getenv("TARGET_IP", "1.1.1.1")
INTERVAL = int(os.getenv("INTERVAL", "30"))
DB_PATH = os.getenv("DB_PATH", "/data/ping_log.db")
CSV_PATH = os.getenv("CSV_PATH", "/data/ping_history.csv")

# Speedtest Adaptive Parameters
SPEED_DEVIATION_THRESHOLD = float(os.getenv("SPEED_DEVIATION_THRESHOLD", "0.10"))  # 10%
SPEED_WINDOW_DAYS = int(os.getenv("SPEED_WINDOW_DAYS", "7"))

# Geometric Progression steps from 1h to 168h in 7 steps: r = (168/1)**(1/6)
_R = 168.0 ** (1.0 / 6.0)
PG_STEPS_HOURS = [round(1.0 * (_R**i), 2) for i in range(7)]
PG_STEPS_HOURS[0] = 1.0
PG_STEPS_HOURS[-1] = 168.0

# Cache for asynchronous traceroute results
_latest_traceroute = "Initializing..."
_traceroute_lock = threading.Lock()

# Locks for thread-safe database and CSV writes
_db_lock = threading.Lock()
_csv_lock = threading.Lock()

# State for speed test scheduler
_speed_lock = threading.Lock()
_speed_running = False
_current_network_key: str | None = None
_step_k = 1  # 1-indexed, from 1 to 7
_step_k_by_ssid: dict[str | None, int] = {}
_next_speedtest_due = datetime.min
_pending_network_trigger: tuple[str, str] | None = None

# GeoIP & VPN exit location cache
_geoip_lock = threading.Lock()
_latest_geoip: dict[str, Any] = {
    "ip": "",
    "city": "",
    "country": "",
    "org": "",
    "is_vpn": False,
    "vpn_provider": "",
}
_last_geoip_fetch: float = 0.0


def _fetch_geoip_worker() -> None:
    """Queries public GeoIP endpoints in the background to identify exit location and provider."""
    global _latest_geoip, _last_geoip_fetch
    endpoints = [
        ("http://ip-api.com/json/", lambda d: {
            "ip": d.get("query", ""),
            "city": d.get("city", ""),
            "country": d.get("countryCode", "") or d.get("country", ""),
            "org": d.get("org", "") or d.get("isp", ""),
        }),
        ("https://ipinfo.io/json", lambda d: {
            "ip": d.get("ip", ""),
            "city": d.get("city", ""),
            "country": d.get("country", ""),
            "org": d.get("org", ""),
        }),
    ]
    for url, parser in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                parsed = parser(data)
                org_lower = parsed.get("org", "").lower()
                is_vpn = any(k in org_lower for k in ("surfshark", "vpn", "m247", "datacamp", "nord", "mullvad", "proton"))
                vpn_provider = "Surfshark" if "surfshark" in org_lower else ("VPN" if is_vpn else "")
                parsed["is_vpn"] = is_vpn
                parsed["vpn_provider"] = vpn_provider
                with _geoip_lock:
                    _latest_geoip = parsed
                    _last_geoip_fetch = time.monotonic()
                return
        except Exception:
            continue


def trigger_geoip_refresh(force: bool = False) -> None:
    """Triggers background GeoIP refresh if cache expired or force requested."""
    global _last_geoip_fetch
    now = time.monotonic()
    if force or (now - _last_geoip_fetch > 300):
        t = threading.Thread(target=_fetch_geoip_worker, daemon=True)
        t.start()


def get_cached_geoip() -> dict[str, Any]:
    with _geoip_lock:
        return dict(_latest_geoip)


def init_storage(db_path: str, csv_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Initialize SQLite schema
    conn = sqlite3.connect(db_path, check_same_thread=False)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ping_log (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                ts                   TEXT    NOT NULL,
                target               TEXT    NOT NULL,
                status               TEXT    NOT NULL,
                latency_ms           REAL,
                jitter_ms            REAL,
                packet_loss_pct      REAL,
                consecutive_failures INTEGER NOT NULL DEFAULT 0,
                network_type         TEXT,
                ssid                 TEXT,
                interface            TEXT,
                gateway_ip           TEXT,
                traceroute           TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON ping_log(ts)")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS speed_log (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                ts             TEXT    NOT NULL,
                ssid           TEXT,
                download_mbps  REAL,
                upload_mbps    REAL,
                ping_ms        REAL,
                server_name    TEXT,
                step_k         INTEGER NOT NULL,
                interval_hours REAL    NOT NULL,
                weekly_mean    REAL,
                deviation_pct  REAL,
                trigger_reason TEXT    NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_speed_ts ON speed_log(ts)")

    # Initialize CSV files with headers if they don't exist
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "target", "status", "latency_ms", "jitter_ms",
                "packet_loss_pct", "consecutive_failures", "network_type",
                "ssid", "interface", "gateway_ip", "traceroute"
            ])

    speed_csv = os.path.join(os.path.dirname(csv_path), "speed_history.csv")
    if not os.path.exists(speed_csv):
        with open(speed_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "ssid", "download_mbps", "upload_mbps",
                "ping_ms", "server", "step_k", "interval_hours",
                "weekly_mean", "deviation_pct", "trigger_reason"
            ])

    return conn


def get_wifi_ssid(interface: str) -> str | None:
    """Retrieves Wi-Fi SSID directly using SIOCGIWESSID wireless ioctl."""
    SIOCGIWESSID = 0x8B1B
    try:
        import array
        import fcntl
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        buf = array.array("B", [0] * 33)
        addr, _ = buf.buffer_info()
        point = addr.to_bytes(8, "little") + (32).to_bytes(2, "little") + (0).to_bytes(2, "little") + (0).to_bytes(4, "little")
        req = interface.encode("utf-8")[:15].ljust(16, b"\0") + point
        fcntl.ioctl(sock.fileno(), SIOCGIWESSID, req)
        ssid = buf.tobytes().split(b"\0")[0].decode("utf-8", errors="ignore").strip()
        return ssid if ssid else None
    except Exception:
        return None


def get_underlying_wifi_ssid() -> str | None:
    """Scans all wireless interfaces to detect connected Wi-Fi SSID, even when routed via VPN."""
    try:
        if os.path.exists("/sys/class/net"):
            for dev in os.listdir("/sys/class/net"):
                if dev.startswith(("wl", "wlan")):
                    ssid = get_wifi_ssid(dev)
                    if ssid:
                        return ssid
    except Exception:
        pass
    return None


def get_network_info() -> tuple[str, str, str, str, str]:
    """
    Detects active route to TARGET_IP, interface, network type (WIFI/LAN/VPN), SSID, and gateway.
    Returns (net_type, network_key, dev, gw, display_name).
    """
    try:
        res = subprocess.run(
            ["ip", "route", "get", TARGET_IP],
            capture_output=True,
            text=True,
            timeout=2,
        )
        tokens = res.stdout.strip().split()
        dev = "UNKNOWN"
        gw = "direct"
        if "dev" in tokens:
            dev = tokens[tokens.index("dev") + 1]
        if "via" in tokens:
            gw = tokens[tokens.index("via") + 1]

        underlying_wifi = get_underlying_wifi_ssid()
        geoip = get_cached_geoip()

        is_vpn_dev = any(k in dev for k in ("wg", "tun", "tap", "vpn", "surfshark"))
        is_vpn = is_vpn_dev or geoip.get("is_vpn", False)

        if is_vpn:
            net_type = "VPN"
            vpn_prov = geoip.get("vpn_provider") or ("Surfshark" if "surfshark" in dev else "VPN")
            loc_parts = []
            if geoip.get("city"):
                loc_parts.append(geoip["city"])
            if geoip.get("country"):
                loc_parts.append(geoip["country"])
            loc_str = f" [{', '.join(loc_parts)}]" if loc_parts else ""

            if underlying_wifi:
                display_name = f"VPN:{vpn_prov}{loc_str} via WIFI [{underlying_wifi}] ({dev})"
                net_key = f"VPN:{vpn_prov}{loc_str} ({underlying_wifi})"
            else:
                display_name = f"VPN:{vpn_prov}{loc_str} ({dev})"
                net_key = f"VPN:{vpn_prov}{loc_str}"
        elif dev.startswith(("wl", "wlan")):
            net_type = "WIFI"
            wifi_ssid = get_wifi_ssid(dev) or underlying_wifi
            ssid_name = wifi_ssid if wifi_ssid else "Wi-Fi"
            display_name = f"WIFI [{ssid_name}]"
            net_key = ssid_name
        elif dev.startswith(("eth", "en")):
            net_type = "LAN"
            display_name = f"LAN ({dev})"
            net_key = f"LAN:{dev}"
        else:
            net_type = "OTHER"
            display_name = f"{dev}"
            net_key = dev

        return net_type, net_key, dev, gw, display_name
    except Exception:
        pass
    return "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN"


def _run_traceroute_worker(host: str, max_hops: int = 5) -> None:
    """Background worker to run traceroute without blocking the main 30s ping loop."""
    global _latest_traceroute
    try:
        cmd = ["traceroute", "-n", "-m", str(max_hops), "-w", "1", "-q", "1", host]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        raw_lines = [l.strip() for l in res.stdout.splitlines()[1:] if l.strip()]

        hops = []
        for line in raw_lines:
            tokens = line.split()
            if len(tokens) >= 2:
                hop_num = tokens[0]
                ip = tokens[1]
                time_str = f"({tokens[2]}ms)" if len(tokens) >= 3 and tokens[2] != "*" else ""
                hops.append(f"{hop_num}:{ip}{time_str}".strip())

        formatted = " -> ".join(hops) if hops else "No route"
        with _traceroute_lock:
            _latest_traceroute = formatted
    except Exception as e:
        with _traceroute_lock:
            _latest_traceroute = f"Traceroute error: {e}"


def trigger_traceroute(host: str) -> None:
    t = threading.Thread(target=_run_traceroute_worker, args=(host,), daemon=True)
    t.start()


def get_cached_traceroute() -> str:
    with _traceroute_lock:
        return _latest_traceroute


def ping_host_icmplib(host: str) -> tuple[bool, float | None, float | None, float]:
    """Pings host using icmplib RAW sockets. Returns (is_alive, avg_rtt, jitter, packet_loss)."""
    try:
        res = icmp_ping(host, count=2, interval=0.5, timeout=2.0, privileged=True)
        if res.is_alive:
            return True, round(res.avg_rtt, 2), round(res.jitter, 2), res.packet_loss
        return False, None, None, res.packet_loss
    except Exception:
        # Fallback to system ping command if RAW socket encounters any issue
        try:
            t0 = time.monotonic()
            ret = subprocess.run(["ping", "-c", "1", "-W", "2", "-s", "0", host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elapsed = (time.monotonic() - t0) * 1000
            if ret.returncode == 0:
                return True, round(elapsed, 2), 0.0, 0.0
        except Exception:
            pass
        return False, None, None, 1.0


def compute_hourly_ffill_weekly_mean(conn: sqlite3.Connection, ssid: str | None, now: datetime) -> float | None:
    """Calculates moving average for the given network SSID using hourly forward-fill (ffill)."""
    cutoff = now - timedelta(days=SPEED_WINDOW_DAYS)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")

    with _db_lock:
        cursor = conn.cursor()
        if ssid:
            cursor.execute(
                """
                SELECT ts, download_mbps
                FROM speed_log
                WHERE ssid = ? AND ts >= ? AND download_mbps > 0
                ORDER BY ts ASC
                """,
                (ssid, cutoff_str),
            )
        else:
            cursor.execute(
                """
                SELECT ts, download_mbps
                FROM speed_log
                WHERE (ssid IS NULL OR ssid = '') AND ts >= ? AND download_mbps > 0
                ORDER BY ts ASC
                """,
                (cutoff_str,),
            )
        rows = cursor.fetchall()

    if not rows:
        return None

    measurements: list[tuple[datetime, float]] = []
    for ts_str, dl in rows:
        try:
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            measurements.append((dt, float(dl)))
        except Exception:
            continue

    if not measurements:
        return None

    # Calculate hourly forward fill only across the active observation window for this network
    start_time = max(cutoff, measurements[0][0])
    total_hours = max(1, int((now - start_time).total_seconds() // 3600))

    hourly_values: list[float] = []
    cur_val = measurements[0][1]
    m_idx = 0

    for h in range(total_hours):
        hour_point = start_time + timedelta(hours=h + 1)
        while m_idx < len(measurements) and measurements[m_idx][0] <= hour_point:
            cur_val = measurements[m_idx][1]
            m_idx += 1
        hourly_values.append(cur_val)

    if not hourly_values:
        return cur_val

    return sum(hourly_values) / len(hourly_values)


def measure_throughput_speedtest() -> tuple[float | None, float | None, float | None, str]:
    """Runs Ookla speedtest-cli benchmark. Returns (dl_mbps, ul_mbps, ping_ms, server_name)."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        dl = round(st.download() / 1_000_000, 2)
        ul = round(st.upload() / 1_000_000, 2)
        server = f"{st.best['sponsor']} ({st.best['name']})"
        ping_res = round(float(st.results.ping), 2)
        return dl, ul, ping_res, server
    except Exception as e:
        return None, None, None, f"Erro: {e}"


def _run_speedtest_worker(conn: sqlite3.Connection, ssid: str | None, reason: str) -> None:
    """Executes speedtest asynchronously and updates adaptive PG schedule for the active network."""
    global _speed_running, _step_k, _next_speedtest_due, _pending_network_trigger, _current_network_key

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        dl, ul, ping_ms, server_name = measure_throughput_speedtest()
        if dl is None:
            with _speed_lock:
                _step_k = 1
                _step_k_by_ssid[ssid] = 1
                _next_speedtest_due = now + timedelta(hours=1)
                _speed_running = False
            return

        weekly_mean = compute_hourly_ffill_weekly_mean(conn, ssid, now)
        is_baseline = weekly_mean is None or weekly_mean <= 0

        if not is_baseline:
            dev_pct = abs(dl - weekly_mean) / weekly_mean
        else:
            weekly_mean = dl
            dev_pct = 0.0

        with _speed_lock:
            cur_k = _step_k_by_ssid.get(ssid, 1)
            old_k = cur_k
            if is_baseline:
                _step_k = 1
                status_str = f"BASELINE INICIAL (primeira medição na rede '{ssid or 'N/A'}': {dl:.2f} Mbps) -> Passo 1 (1h)"
            elif dev_pct > SPEED_DEVIATION_THRESHOLD:
                _step_k = 1
                status_str = f"INSTÁVEL (desvio {dev_pct*100:.1f}% > 10% da média {weekly_mean:.2f} Mbps na rede '{ssid or 'N/A'}') -> Reseta para Passo 1 (1h)"
            else:
                _step_k = min(7, cur_k + 1)
                status_str = f"ESTÁVEL (desvio {dev_pct*100:.1f}% <= 10% da média {weekly_mean:.2f} Mbps na rede '{ssid or 'N/A'}') -> Passo {old_k} -> {_step_k}"

            _step_k_by_ssid[ssid] = _step_k
            hours = PG_STEPS_HOURS[_step_k - 1]
            _next_speedtest_due = now + timedelta(hours=hours)

        # 1. Save to SQLite
        with _db_lock, conn:
            conn.execute(
                """
                INSERT INTO speed_log (
                    ts, ssid, download_mbps, upload_mbps, ping_ms, server_name,
                    step_k, interval_hours, weekly_mean, deviation_pct, trigger_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (now_str, ssid, dl, ul, ping_ms, server_name, _step_k, hours, round(weekly_mean, 2), round(dev_pct * 100, 2), reason),
            )

        # 2. Append to CSV
        speed_csv = os.path.join(os.path.dirname(CSV_PATH), "speed_history.csv")
        with _csv_lock, open(speed_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                now_str, ssid, dl, ul, ping_ms, server_name,
                _step_k, hours, round(weekly_mean, 2), round(dev_pct * 100, 2), reason
            ])

        print(
            f"[{now_str}] 🚀 SPEEDTEST [{ssid or 'N/A'}] Motivo: {reason} | Servidor: {server_name} | "
            f"DL: {dl} Mbps, UL: {ul} Mbps, Ping: {ping_ms}ms | {status_str} | Próximo em {hours}h",
            flush=True,
        )

    finally:
        pending = None
        with _speed_lock:
            _speed_running = False
            if _pending_network_trigger is not None:
                pending = _pending_network_trigger
                _pending_network_trigger = None
                _current_network_key = pending[0]
                _speed_running = True

        if pending is not None:
            # Immediately trigger next speedtest for the queued network change
            t = threading.Thread(
                target=_run_speedtest_worker,
                args=(conn, pending[0], pending[1]),
                daemon=True,
            )
            t.start()


def check_and_trigger_speedtest(
    conn: sqlite3.Connection,
    current_network: str | None,
    force_reconnect: bool = False,
) -> None:
    """Verifies network changes or scheduled due dates and triggers speedtest worker."""
    global _current_network_key, _step_k, _next_speedtest_due, _speed_running, _pending_network_trigger

    if not current_network or current_network == "UNKNOWN":
        return

    now = datetime.now()
    should_run = False
    reason = ""

    with _speed_lock:
        network_changed = (_current_network_key is not None and current_network != _current_network_key)
        initial_network = (_current_network_key is None)

        if network_changed:
            should_run = True
            reason = f"Troca de rede: '{_current_network_key}' -> '{current_network}'"
            _step_k_by_ssid[current_network] = 1
        elif initial_network:
            should_run = True
            reason = f"Inicialização na rede '{current_network}'"
            _step_k_by_ssid[current_network] = 1
        elif force_reconnect:
            should_run = True
            reason = f"Reconexão após queda de link na rede '{current_network}'"
        elif now >= _next_speedtest_due:
            cur_k = _step_k_by_ssid.get(current_network, _step_k)
            _step_k = cur_k
            should_run = True
            reason = f"Agendamento Passo {_step_k} ({PG_STEPS_HOURS[_step_k - 1]}h atingido)"

        if should_run:
            if _speed_running:
                # Queue the network change if a test is already running
                if network_changed or initial_network or force_reconnect:
                    _pending_network_trigger = (current_network, reason)
                return

            _current_network_key = current_network
            _speed_running = True

    if should_run:
        t = threading.Thread(
            target=_run_speedtest_worker,
            args=(conn, current_network, reason),
            daemon=True,
        )
        t.start()


def log_ping(
    conn: sqlite3.Connection,
    ts: str,
    status: str,
    latency: float | None,
    jitter: float | None,
    packet_loss: float,
    failures: int,
    net_type: str,
    ssid: str | None,
    interface: str,
    gateway: str,
    trace: str,
) -> None:
    # 1. SQLite Insert
    with _db_lock:
        with conn:
            conn.execute(
                """
                INSERT INTO ping_log (
                    ts, target, status, latency_ms, jitter_ms, packet_loss_pct,
                    consecutive_failures, network_type, ssid, interface, gateway_ip, traceroute
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (ts, TARGET_IP, status, latency, jitter, packet_loss, failures, net_type, ssid, interface, gateway, trace),
            )

    # 2. CSV Append
    with _csv_lock:
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                ts, TARGET_IP, status, latency, jitter, packet_loss,
                failures, net_type, ssid, interface, gateway, trace
            ])


def main() -> None:
    conn = init_storage(DB_PATH, CSV_PATH)
    consecutive_failures = 0
    cycle_count = 0

    print(
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Monitor icmplib & speedtest-cli iniciado "
        f"(alvo={TARGET_IP}, ping_interval={INTERVAL}s, db={DB_PATH}, csv={CSV_PATH})",
        flush=True,
    )

    trigger_traceroute(TARGET_IP)
    trigger_geoip_refresh(force=True)

    last_network_key: str | None = None

    while True:
        cycle_count += 1
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_up, latency, jitter, loss = ping_host_icmplib(TARGET_IP)
        net_type, net_key, iface, gateway, display_name = get_network_info()

        was_restored = False
        if is_up:
            if consecutive_failures >= 2:
                was_restored = True
                print(f"[{ts}] 🟢 RESTORED after {consecutive_failures} consecutive failures.", flush=True)
            consecutive_failures = 0

            # Force GeoIP refresh if network changed
            if last_network_key is not None and net_key != last_network_key:
                trigger_geoip_refresh(force=True)
            last_network_key = net_key

            check_and_trigger_speedtest(conn, net_key, force_reconnect=was_restored)
        else:
            consecutive_failures += 1
            print(f"[{ts}] ❌ DOWN (failure #{consecutive_failures}) | {display_name} ({iface}) | Trace: {get_cached_traceroute()}", flush=True)
            if consecutive_failures == 3:
                print(f"[{ts}] 🚨 ALERT: Outage confirmed (3 consecutive failures).", flush=True)
            log_ping(conn, ts, "DOWN", None, None, 100.0, consecutive_failures, net_type, net_key, iface, gateway, get_cached_traceroute())

        if not is_up or (cycle_count % 10 == 0):
            trigger_traceroute(TARGET_IP)
        if cycle_count % 10 == 0:
            trigger_geoip_refresh()

        trace = get_cached_traceroute()
        geoip = get_cached_geoip()
        geo_info = f" | IP: {geoip['ip']} ({geoip['city']}, {geoip['country']} - {geoip['org']})" if geoip.get("ip") else ""

        if is_up:
            jitter_str = f" | Jitter: {jitter}ms" if jitter is not None else ""
            print(f"[{ts}] ✅ UP   ({latency}ms{jitter_str}) | {display_name} ({iface} -> {gateway}){geo_info}", flush=True)
            log_ping(conn, ts, "UP", latency, jitter, loss, consecutive_failures, net_type, net_key, iface, gateway, trace)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
