import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "data" / "ping_log.db"


def show_records(limit: int = 15) -> None:
    if not DB_FILE.exists():
        print(f"O banco de dados ainda não foi criado em: {DB_FILE}")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM ping_log")
        total_pings = cursor.fetchone()[0]

        print(f"\n=== PING LOG (Total: {total_pings} registros | Últimos {limit}) ===")
        print(f"{'ID':<5} | {'Timestamp':<19} | {'Status':<6} | {'Latência':<9} | {'Rede':<6} | {'SSID':<15} | {'Interface':<10} | {'Gateway':<15} | {'Traceroute'}")
        print("-" * 135)

        cursor.execute(
            """
            SELECT id, ts, status, latency_ms, network_type, ssid, interface, gateway_ip, traceroute 
            FROM ping_log 
            ORDER BY id DESC 
            LIMIT ?
            """,
            (limit,),
        )

        for row in cursor.fetchall():
            row_id, ts, status, latency, net_type, ssid, iface, gw, trace = row
            lat_str = f"{latency}ms" if latency is not None else "N/A"
            net_type = net_type or "N/A"
            ssid = ssid or "N/A"
            iface = iface or "N/A"
            gw = gw or "N/A"
            trace = trace or "N/A"
            if len(trace) > 45:
                trace = trace[:42] + "..."
            print(f"{row_id:<5} | {ts:<19} | {status:<6} | {lat_str:<9} | {net_type:<6} | {ssid:<15} | {iface:<10} | {gw:<15} | {trace}")

        # Check speed_log
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='speed_log'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM speed_log")
            total_speeds = cursor.fetchone()[0]

            print(f"\n=== SPEEDTEST LOG (Total: {total_speeds} testes | Últimos {limit}) ===")
            print(f"{'ID':<4} | {'Timestamp':<19} | {'SSID':<12} | {'Download':<11} | {'Upload':<11} | {'Passo':<6} | {'Prox':<6} | {'Média 7d':<10} | {'Desvio':<7} | {'Motivo'}")
            print("-" * 135)

            cursor.execute(
                """
                SELECT id, ts, ssid, download_mbps, upload_mbps, step_k, interval_hours, weekly_mean, deviation_pct, trigger_reason
                FROM speed_log
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )

            for row in cursor.fetchall():
                sid, ts, ssid, dl, ul, k, intv, mean, dev, reason = row
                dl_str = f"{dl:.2f} Mbps" if dl is not None else "N/A"
                ul_str = f"{ul:.2f} Mbps" if ul is not None else "N/A"
                mean_str = f"{mean:.2f} Mbps" if mean is not None else "N/A"
                dev_str = f"{dev:.1f}%" if dev is not None else "N/A"
                print(f"{sid:<4} | {ts:<19} | {str(ssid):<12} | {dl_str:<11} | {ul_str:<11} | k={k:<4} | {intv}h   | {mean_str:<10} | {dev_str:<7} | {reason}")

    finally:
        conn.close()


if __name__ == "__main__":
    show_records()
