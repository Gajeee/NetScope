"""
packets.py
The Capture / Packets page: interface selector, start/pause/stop/clear
controls, a live packet table with a Wireshark-style filter bar, and a
detail panel for the selected packet. Controls are plain, labeled
pill buttons and a custom-painted status dot — no emoji glyphs.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QTextEdit, QAbstractItemView,
)
from PySide6.QtCore import Qt

from capture.sniffer import CaptureThread, list_interfaces
from ui.widgets import Card, StatusIndicator, SUCCESS, DANGER, MUTED


PACKET_LIMIT = 5000  # cap rows kept in the live table for UI performance


class PacketsPage(QWidget):
    def __init__(self, storage, on_packet_callback=None, on_log=None):
        super().__init__()
        self.setObjectName("RootCanvas")
        self.storage = storage
        self.on_packet_callback = on_packet_callback
        self.on_log = on_log or (lambda msg: None)

        self.capture_thread: CaptureThread | None = None
        self.all_rows: list[dict] = []
        self.is_paused = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 26, 28, 26)
        outer.setSpacing(16)

        title = QLabel("Capture")
        title.setObjectName("SectionTitle")
        outer.addWidget(title)

        # --- Control bar ---
        control_card = Card(padding=16)
        control_row = QHBoxLayout()
        control_row.setSpacing(12)

        iface_label = QLabel("Interface")
        iface_label.setStyleSheet("color:#8A8A8E;")
        control_row.addWidget(iface_label)

        self.iface_combo = QComboBox()
        self.iface_combo.addItems(list_interfaces() or ["Wi-Fi", "Ethernet"])
        self.iface_combo.setFixedWidth(160)
        control_row.addWidget(self.iface_combo)

        self.status = StatusIndicator("Ready", MUTED)
        control_row.addSpacing(8)
        control_row.addWidget(self.status)

        control_row.addStretch()

        self.btn_start = QPushButton("Start Capture")
        self.btn_start.setObjectName("Primary")
        self.btn_start.clicked.connect(self.start_capture)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setObjectName("Danger")
        self.btn_stop.clicked.connect(self.stop_capture)
        self.btn_stop.setEnabled(False)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setObjectName("Ghost")
        self.btn_clear.clicked.connect(self.clear_packets)

        for b in (self.btn_start, self.btn_pause, self.btn_stop, self.btn_clear):
            control_row.addWidget(b)

        control_card.addLayout(control_row)
        outer.addWidget(control_card)

        # --- Filter bar ---
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(
            "Filter packets  ·  tcp, udp port 443, dns, 192.168.1.1"
        )
        self.filter_input.textChanged.connect(self.apply_filter)
        outer.addWidget(self.filter_input)

        # --- Table + detail panel ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(18)
        splitter.setChildrenCollapsible(False)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Time", "Source", "Destination", "Protocol", "Length", "Info"]
        )
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemSelectionChanged.connect(self.show_details)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)

        detail_card = Card(padding=18)
        detail_title = QLabel("PACKET DETAILS")
        detail_title.setObjectName("CardLabel")
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setPlaceholderText("Select a packet to view details")
        detail_card.addWidget(detail_title)
        detail_card.addWidget(self.detail_text)

        splitter.addWidget(self.table)
        splitter.addWidget(detail_card)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        outer.addWidget(splitter, 1)

    # ------------------------------------------------------------------
    # Capture controls
    # ------------------------------------------------------------------
    def start_capture(self):
        if self.capture_thread and self.capture_thread.isRunning():
            return

        bpf = self._filter_to_bpf(self.filter_input.text())
        iface = self.iface_combo.currentText()

        self.capture_thread = CaptureThread(interface=iface, bpf_filter=bpf)
        self.capture_thread.packet_captured.connect(self._add_packet)
        self.capture_thread.error.connect(self._on_error)
        self.capture_thread.stopped.connect(self._on_stopped)
        self.capture_thread.start()

        self.is_paused = False
        self.status.set_state("Capturing", SUCCESS, glow=True)
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_pause.setText("Pause")
        self.btn_stop.setEnabled(True)
        self.on_log("Capture started")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.btn_pause.setText("Resume" if self.is_paused else "Pause")
        if self.is_paused:
            self.status.set_state("Paused", MUTED)
        else:
            self.status.set_state("Capturing", SUCCESS, glow=True)
        self.on_log("Capture paused" if self.is_paused else "Capture resumed")

    def stop_capture(self):
        if self.capture_thread:
            self.capture_thread.stop()
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.status.set_state("Stopped", DANGER)
        self.on_log("Capture stopped")

    def clear_packets(self):
        self.all_rows.clear()
        self.table.setRowCount(0)
        self.detail_text.clear()
        self.storage.clear()
        self.on_log("Packets cleared")

    def _on_error(self, message: str):
        self.on_log(f"Error: {message}")
        self.status.set_state("Error", DANGER)
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)

    def _on_stopped(self):
        if self.status.label.text() != "Error":
            self.status.set_state("Stopped", DANGER)

    # ------------------------------------------------------------------
    # Packet handling
    # ------------------------------------------------------------------
    def _add_packet(self, info: dict):
        if self.is_paused:
            return

        self.all_rows.append(info)
        if len(self.all_rows) > PACKET_LIMIT:
            self.all_rows.pop(0)

        self.storage.save_packet(info)

        if self.on_packet_callback:
            self.on_packet_callback(info)

        if self._matches_filter(info, self.filter_input.text()):
            self._append_row(info)

    def _append_row(self, info: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        info_text = info.get("raw_summary", "")
        if info.get("http_method"):
            info_text = f"{info['http_method']} {info.get('http_path', '')}"

        values = [
            info.get("time", ""),
            info.get("source", ""),
            info.get("destination", ""),
            info.get("protocol", ""),
            str(info.get("length", "")),
            info_text,
        ]
        for col, val in enumerate(values):
            item = QTableWidgetItem(val)
            item.setData(Qt.UserRole, info)
            self.table.setItem(row, col, item)

        self.table.scrollToBottom()

    def show_details(self):
        items = self.table.selectedItems()
        if not items:
            return
        info = items[0].data(Qt.UserRole)
        if not info:
            return

        lines = [
            f"Packet #{info.get('index')}",
            "",
            "Ethernet",
            f"  Source MAC: {info.get('src_mac')}",
            f"  Destination MAC: {info.get('dst_mac')}",
            "",
            "IP",
            f"  Source: {info.get('source')}",
            f"  Destination: {info.get('destination')}",
            "",
            info.get("protocol", ""),
        ]
        if info.get("sport") is not None:
            lines.append(f"  Source Port: {info.get('sport')}")
        if info.get("dport") is not None:
            lines.append(f"  Destination Port: {info.get('dport')}")
        if info.get("flags"):
            lines.append(f"  Flags: {info.get('flags')}")
        if info.get("http_method"):
            lines += [
                "",
                "HTTP",
                f"  Method: {info.get('http_method')}",
                f"  Host: {info.get('http_host')}",
                f"  Path: {info.get('http_path')}",
            ]
        self.detail_text.setPlainText("\n".join(lines))

    # ------------------------------------------------------------------
    # Filtering (a very small Wireshark-like BPF-ish filter subset)
    # ------------------------------------------------------------------
    def apply_filter(self, text: str):
        self.table.setRowCount(0)
        for info in self.all_rows:
            if self._matches_filter(info, text):
                self._append_row(info)

    def _matches_filter(self, info: dict, text: str) -> bool:
        text = (text or "").strip().lower()
        if not text:
            return True

        tokens = text.split()
        proto = (info.get("protocol") or "").lower()

        for tok in tokens:
            if tok in ("tcp", "udp", "dns", "icmp"):
                if proto != tok:
                    return False
            elif tok == "http":
                if not info.get("http_method"):
                    return False
            elif tok.startswith("port"):
                continue  # handled below combined with number
            elif tok.isdigit():
                port = int(tok)
                if info.get("sport") != port and info.get("dport") != port:
                    return False
            elif "." in tok:  # looks like an IP fragment
                if tok not in (info.get("source", "") + info.get("destination", "")).lower():
                    return False
            else:
                haystack = " ".join(
                    str(info.get(k, "")) for k in
                    ("source", "destination", "protocol", "http_host", "http_path")
                ).lower()
                if tok not in haystack:
                    return False
        return True

    def _filter_to_bpf(self, text: str) -> str:
        """Best-effort translation of the simple UI filter into a BPF string
        scapy/libpcap understands, for pre-filtering at capture time.
        Falls back to no filter if the text doesn't look like valid BPF."""
        text = (text or "").strip().lower()
        if not text:
            return ""
        simple_protocols = {"tcp", "udp", "icmp"}
        if text in simple_protocols:
            return text
        if text.startswith("port ") or text.startswith("ip "):
            return text
        if text == "dns":
            return "udp port 53"
        if text == "http":
            return "tcp port 80"
        return ""
