# NetScope — Minimal Network Packet Analyzer

A lightweight, Mini-Wireshark-style desktop app for monitoring **your own
machine's** network traffic in real time. Clean black-and-white UI,
built as a cybersecurity learning / portfolio project.

> This tool only captures traffic visible on the network interfaces of
> the computer it runs on — the same category of software as Wireshark,
> tcpdump, or your OS's built-in resource monitor. It is not designed
> and should not be used to monitor networks or devices you don't own
> or have explicit permission to inspect.

---

## Features

- Live dashboard: packets/sec, throughput estimate, active connections
- Protocol usage bars (TCP / UDP / DNS / HTTP / ICMP)
- Packet table with a Wireshark-style filter bar (`tcp`, `udp port 443`, `dns`, IP fragments, etc.)
- Click-through packet detail panel (Ethernet / IP / TCP-UDP / plaintext HTTP)
- Start / Pause / Stop / Clear capture controls
- SQLite storage of every captured packet for the session
- JSON export and a summary PDF (or .txt fallback) report
- Basic security heuristics (failed-connection spikes, ICMP floods, DNS bursts)
- Settings page (startup capture, save folder, default interface)
- Strict black (`#000000`) / white (`#FFFFFF`) / grey (`#AAAAAA`) theme, no gradients

## Project structure

```
NetScope/
├── main.py                 # entry point + startup screen
├── capture/
│   ├── sniffer.py          # QThread wrapper around Scapy sniff()
│   └── protocols.py        # raw packet -> dict parser
├── ui/
│   ├── main_window.py      # sidebar + page routing + menu bar
│   ├── dashboard.py        # live stats, graph, protocol bars
│   ├── packets.py          # capture controls, table, filters, details
│   ├── stats_reports.py    # Statistics + Reports pages
│   ├── settings.py         # Settings + About
│   └── theme.py            # black & white QSS stylesheet
├── database/
│   └── storage.py          # SQLite storage, JSON/report export
├── exports/                # default location for exported files
├── assets/                 # icons / logo (add your own logo.png here)
├── requirements.txt
└── README.md
```

## Setup

Requires **Python 3.10+** (3.12 recommended).

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Windows — install Npcap

Live capture on Windows needs [Npcap](https://npcap.com/#download)
(install with the "WinPcap API-compatible mode" option checked).

### macOS / Linux — permissions

Raw packet capture needs elevated privileges:

```bash
sudo python main.py
```

Or, on Linux, grant the capability once so you don't need `sudo` every time:

```bash
sudo setcap cap_net_raw,cap_net_admin=eip $(readlink -f $(which python3))
```

## Run

```bash
python main.py
```

1. The startup screen checks adapters and loads the database.
2. Pick a network interface from the dropdown on the Capture page.
3. Press **Start** to begin capturing your own traffic live.
4. Use the filter bar, click a packet for details, and export a report when done.

## Building a standalone executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name NetScope main.py
```

- Windows → `dist/NetScope.exe`
- macOS → `dist/NetScope` (wrap in a `.app` bundle with `--windowed` + `py2app` if you want a full macOS bundle)
- Linux → `dist/NetScope`

Double-click (or run) the output to launch NetScope without a Python install.

## Notes & limitations

- HTTPS/TLS traffic is shown at the IP/TCP level only — payloads stay
  encrypted, as they should. The HTTP analyzer only parses plaintext
  HTTP (port 80) requests already visible on the wire.
- The "Country" and geo-IP style fields are left as placeholders; wiring
  up a GeoIP database is a good next step if you want to extend it.
- The Download/Upload figures on the dashboard are a lightweight
  estimate based on packet rate, not a precise byte-accurate meter —
  swap in real per-interface byte counters (e.g. `psutil.net_io_counters`)
  if you want exact throughput.
