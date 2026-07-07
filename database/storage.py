"""
storage.py
SQLite-backed storage for captured packets, plus JSON export and a very
simple text-based PDF-style report (built with reportlab if available,
otherwise falls back to a .txt report so the feature never hard-fails).
"""

import json
import os
import sqlite3
import time

DB_PATH = os.path.join(os.path.dirname(__file__), "netscope.db")


class Storage:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capture_index INTEGER,
                time TEXT,
                timestamp REAL,
                source TEXT,
                destination TEXT,
                protocol TEXT,
                length INTEGER,
                sport INTEGER,
                dport INTEGER,
                flags TEXT,
                src_mac TEXT,
                dst_mac TEXT,
                http_method TEXT,
                http_host TEXT,
                http_path TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def save_packet(self, info: dict):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO packets
            (capture_index, time, timestamp, source, destination, protocol,
             length, sport, dport, flags, src_mac, dst_mac,
             http_method, http_host, http_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                info.get("index"),
                info.get("time"),
                info.get("timestamp"),
                info.get("source"),
                info.get("destination"),
                info.get("protocol"),
                info.get("length"),
                info.get("sport"),
                info.get("dport"),
                info.get("flags"),
                info.get("src_mac"),
                info.get("dst_mac"),
                info.get("http_method"),
                info.get("http_host"),
                info.get("http_path"),
            ),
        )
        conn.commit()
        conn.close()

    def all_packets(self) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM packets ORDER BY id ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def clear(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM packets")
        conn.commit()
        conn.close()

    def export_json(self, out_path: str):
        packets = self.all_packets()
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(packets, f, indent=2)
        return out_path

    def export_report(self, out_path: str):
        """Generate a simple readable report. Uses reportlab for a real PDF
        if it's installed, otherwise writes a plain-text report."""
        packets = self.all_packets()
        total = len(packets)
        proto_counts: dict[str, int] = {}
        total_bytes = 0
        for p in packets:
            proto_counts[p["protocol"]] = proto_counts.get(p["protocol"], 0) + 1
            total_bytes += p.get("length") or 0

        lines = [
            "NetScope Network Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Total Packets: {total}",
            f"Data Transferred: {total_bytes} bytes",
            "",
            "Protocol Breakdown:",
        ]
        for proto, count in sorted(proto_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {proto}: {count}")

        lines.append("")
        lines.append("Top Connections:")
        conn_counts: dict[str, int] = {}
        for p in packets:
            key = f"{p['source']} -> {p['destination']}"
            conn_counts[key] = conn_counts.get(key, 0) + 1
        for key, count in sorted(conn_counts.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  {key}: {count} packets")

        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            c = canvas.Canvas(out_path, pagesize=letter)
            width, height = letter
            y = height - 50
            for line in lines:
                c.drawString(50, y, line)
                y -= 16
                if y < 50:
                    c.showPage()
                    y = height - 50
            c.save()
            return out_path
        except Exception:
            txt_path = out_path.rsplit(".", 1)[0] + ".txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return txt_path
