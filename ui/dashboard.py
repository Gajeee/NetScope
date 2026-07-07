"""
dashboard.py
The main Dashboard page: live stats, protocol usage, and a minimal
live packets/sec graph. Uses elevated Card surfaces and custom-painted
MeterBar widgets instead of ASCII/emoji glyphs.
"""

from collections import deque

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer

from ui.widgets import Card, MeterBar

try:
    import pyqtgraph as pg
    pg.setConfigOption("background", "#111113")
    pg.setConfigOption("foreground", "#8A8A8E")
except Exception:  # pragma: no cover
    pg = None


def make_stat_card(label_text: str) -> tuple[Card, QLabel]:
    card = Card(padding=18)
    value_label = QLabel("0")
    value_label.setObjectName("CardValue")
    caption = QLabel(label_text.upper())
    caption.setObjectName("CardLabel")
    card.addWidget(value_label)
    card.addWidget(caption)
    return card, value_label


class ProtocolRow(QWidget):
    """A single 'PROTOCOL  [meter]  count' row, replacing ASCII bars."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(12)

        self.name_label = QLabel(name)
        self.name_label.setFixedWidth(52)
        self.name_label.setStyleSheet("color:#8A8A8E; font-weight:600; font-size:11px;")

        self.meter = MeterBar(height=7)
        self.meter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.count_label = QLabel("0")
        self.count_label.setFixedWidth(46)
        self.count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.count_label.setStyleSheet("font-weight:600;")

        layout.addWidget(self.name_label)
        layout.addWidget(self.meter, 1)
        layout.addWidget(self.count_label)

    def set_count(self, count: int, max_count: int):
        ratio = 0.0 if max_count == 0 else count / max_count
        self.meter.set_ratio(ratio)
        self.count_label.setText(str(count))


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("RootCanvas")
        self._history = deque(maxlen=60)
        self._last_second_count = 0
        self._packet_total = 0
        self._connections = set()
        self._protocol_counts = {"TCP": 0, "UDP": 0, "DNS": 0, "HTTP": 0, "ICMP": 0}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 26, 28, 26)
        outer.setSpacing(20)

        title = QLabel("Dashboard")
        title.setObjectName("SectionTitle")
        outer.addWidget(title)

        # --- Stat cards ---
        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)

        self.card_packets, self.val_packets = make_stat_card("Packets")
        self.card_download, self.val_download = make_stat_card("Download")
        self.card_upload, self.val_upload = make_stat_card("Upload")
        self.card_conns, self.val_conns = make_stat_card("Active Connections")

        cards_layout.addWidget(self.card_packets, 0, 0)
        cards_layout.addWidget(self.card_download, 0, 1)
        cards_layout.addWidget(self.card_upload, 0, 2)
        cards_layout.addWidget(self.card_conns, 0, 3)
        outer.addLayout(cards_layout)

        # --- Graph + protocol usage side by side ---
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(16)

        graph_card = Card(padding=20)
        graph_title = QLabel("NETWORK ACTIVITY  ·  PACKETS / SEC")
        graph_title.setObjectName("CardLabel")
        graph_card.addWidget(graph_title)

        if pg is not None:
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground(None)
            self.plot_widget.showGrid(x=False, y=False)
            self.plot_widget.setMouseEnabled(x=False, y=False)
            self.plot_widget.hideAxis("bottom")
            self.plot_widget.hideAxis("left")
            self.plot_widget.setStyleSheet("border: none; background: transparent;")
            pen = pg.mkPen(color="#F5F5F5", width=2.4)
            self.plot_curve = self.plot_widget.plot([], [], pen=pen)
            fill = pg.FillBetweenItem(
                self.plot_curve,
                pg.PlotCurveItem([0, 1], [0, 0]),
                brush=pg.mkBrush(255, 255, 255, 20),
            )
            self.plot_widget.addItem(fill)
            graph_card.addWidget(self.plot_widget)
        else:
            self.plot_widget = None
            graph_card.addWidget(QLabel("pyqtgraph not available"))

        proto_card = Card(padding=20)
        proto_title = QLabel("PROTOCOL USAGE")
        proto_title.setObjectName("CardLabel")
        proto_card.addWidget(proto_title)

        self.protocol_bars = {}
        for proto in ["TCP", "UDP", "DNS", "HTTP", "ICMP"]:
            row = ProtocolRow(proto)
            self.protocol_bars[proto] = row
            proto_card.addWidget(row)
        proto_card.layout_.addStretch()

        mid_layout.addWidget(graph_card, 2)
        mid_layout.addWidget(proto_card, 1)
        outer.addLayout(mid_layout, 1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def reset(self):
        self._history.clear()
        self._last_second_count = 0
        self._packet_total = 0
        self._connections.clear()
        for proto in self._protocol_counts:
            self._protocol_counts[proto] = 0
        self.val_packets.setText("0")
        self.val_download.setText("0 KB/s")
        self.val_upload.setText("0 KB/s")
        self.val_conns.setText("0")
        for row in self.protocol_bars.values():
            row.set_count(0, 1)
        if self.plot_widget is not None:
            self.plot_curve.setData([], [])

    def on_packet(self, info: dict):
        self._packet_total += 1
        self._last_second_count += 1

        proto = info.get("protocol", "OTHER")
        if info.get("http_method"):
            proto = "HTTP"
        if proto in self._protocol_counts:
            self._protocol_counts[proto] += 1

        conn_key = (info.get("source"), info.get("destination"))
        self._connections.add(conn_key)

        self.val_packets.setText(f"{self._packet_total:,}")
        self.val_conns.setText(str(len(self._connections)))

        max_count = max(self._protocol_counts.values()) or 1
        for proto_name, row in self.protocol_bars.items():
            row.set_count(self._protocol_counts[proto_name], max_count)

    def _tick(self):
        self._history.append(self._last_second_count)
        kb = (self._last_second_count * 512) / 1024
        self.val_download.setText(f"{kb:.1f} KB/s")
        self.val_upload.setText(f"{kb * 0.15:.1f} KB/s")
        self._last_second_count = 0

        if self.plot_widget is not None:
            xs = list(range(len(self._history)))
            self.plot_curve.setData(xs, list(self._history))
