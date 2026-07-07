"""
sniffer.py
The Capture Engine. Wraps Scapy's sniffing in a QThread so the UI never
freezes, and emits a Qt signal for every packet that is captured.

Only captures traffic visible to the local machine's own network
interface(s) -- this is a personal diagnostic tool, the same category
of software as Wireshark, tcpdump, or Windows Resource Monitor.
"""

from PySide6.QtCore import QThread, Signal

from capture.protocols import parse_packet

try:
    from scapy.all import sniff, get_if_list
except Exception:  # pragma: no cover
    sniff = None
    get_if_list = None


class CaptureThread(QThread):
    packet_captured = Signal(dict)
    error = Signal(str)
    stopped = Signal()

    def __init__(self, interface: str | None = None, bpf_filter: str = ""):
        super().__init__()
        self.interface = interface
        self.bpf_filter = bpf_filter
        self._running = False
        self._count = 0

    def run(self):
        if sniff is None:
            self.error.emit(
                "Scapy / Npcap not available. Install scapy and, on Windows, "
                "Npcap (https://npcap.com) to enable live capture."
            )
            return

        self._running = True
        try:
            sniff(
                iface=self.interface if self.interface else None,
                filter=self.bpf_filter or None,
                prn=self._on_packet,
                stop_filter=lambda _pkt: not self._running,
                store=False,
            )
        except PermissionError:
            self.error.emit(
                "Permission denied. Run NetScope as Administrator / with sudo "
                "to capture live packets."
            )
        except Exception as exc:  # noqa: BLE001
            self.error.emit(f"Capture error: {exc}")
        finally:
            self.stopped.emit()

    def _on_packet(self, pkt):
        if not self._running:
            return
        self._count += 1
        try:
            info = parse_packet(pkt, self._count)
            self.packet_captured.emit(info)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(f"Parse error: {exc}")

    def stop(self):
        self._running = False


def list_interfaces() -> list[str]:
    """Return a list of available network interface names."""
    if get_if_list is None:
        return ["Wi-Fi", "Ethernet"]
    try:
        return get_if_list()
    except Exception:
        return ["Wi-Fi", "Ethernet"]
