"""
protocols.py
Parses raw Scapy packets into simple, UI-friendly dictionaries.
"""

import time

try:
    from scapy.all import IP, IPv6, TCP, UDP, ICMP, DNS, Ether, Raw
except Exception:  # pragma: no cover - allows import without npcap installed
    IP = IPv6 = TCP = UDP = ICMP = DNS = Ether = Raw = None


def _safe_mac(pkt):
    src_mac = dst_mac = "N/A"
    if Ether and pkt.haslayer(Ether):
        src_mac = pkt[Ether].src
        dst_mac = pkt[Ether].dst
    return src_mac, dst_mac


def parse_packet(pkt, index: int) -> dict:
    """Convert a scapy packet into a flat dict used everywhere in the UI."""

    info = {
        "index": index,
        "time": time.strftime("%H:%M:%S"),
        "timestamp": time.time(),
        "source": "N/A",
        "destination": "N/A",
        "protocol": "OTHER",
        "length": len(pkt),
        "sport": None,
        "dport": None,
        "flags": "",
        "src_mac": "N/A",
        "dst_mac": "N/A",
        "http_method": None,
        "http_host": None,
        "http_path": None,
        "raw_summary": pkt.summary() if hasattr(pkt, "summary") else str(pkt),
    }

    info["src_mac"], info["dst_mac"] = _safe_mac(pkt)

    ip_layer = None
    if IP and pkt.haslayer(IP):
        ip_layer = pkt[IP]
    elif IPv6 and pkt.haslayer(IPv6):
        ip_layer = pkt[IPv6]

    if ip_layer is not None:
        info["source"] = ip_layer.src
        info["destination"] = ip_layer.dst

    if TCP and pkt.haslayer(TCP):
        tcp = pkt[TCP]
        info["protocol"] = "TCP"
        info["sport"] = tcp.sport
        info["dport"] = tcp.dport
        info["flags"] = str(tcp.flags)

        # very small, safe HTTP peek (plaintext only, no decryption of TLS)
        if Raw and pkt.haslayer(Raw) and (tcp.sport == 80 or tcp.dport == 80):
            try:
                payload = bytes(pkt[Raw].load)
                text = payload.decode(errors="ignore")
                first_line = text.split("\r\n", 1)[0]
                parts = first_line.split(" ")
                if len(parts) >= 2 and parts[0] in (
                    "GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"
                ):
                    info["http_method"] = parts[0]
                    info["http_path"] = parts[1]
                for line in text.split("\r\n"):
                    if line.lower().startswith("host:"):
                        info["http_host"] = line.split(":", 1)[1].strip()
            except Exception:
                pass

    elif UDP and pkt.haslayer(UDP):
        udp = pkt[UDP]
        info["protocol"] = "UDP"
        info["sport"] = udp.sport
        info["dport"] = udp.dport
        if DNS and pkt.haslayer(DNS):
            info["protocol"] = "DNS"

    elif ICMP and pkt.haslayer(ICMP):
        info["protocol"] = "ICMP"

    return info
