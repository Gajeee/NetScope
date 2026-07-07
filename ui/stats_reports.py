"""
stats_reports.py
Statistics page (totals + security alerts) and Reports page (export
buttons for JSON / report). Alerts use a small colored dot + label row
instead of a warning emoji.
"""

import os
import time

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox,
)

from ui.widgets import Card, StatusDot, WARNING, MUTED


class AlertRow(QWidget):
    def __init__(self, text: str):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        layout.addWidget(StatusDot(WARNING, diameter=7))
        label = QLabel(text)
        label.setStyleSheet("color: #E7E7E7;")
        layout.addWidget(label)
        layout.addStretch()


class StatisticsPage(QWidget):
    def __init__(self, storage):
        super().__init__()
        self.setObjectName("RootCanvas")
        self.storage = storage
        self.start_time = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 26, 28, 26)
        outer.setSpacing(20)

        title = QLabel("Statistics")
        title.setObjectName("SectionTitle")
        outer.addWidget(title)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        self.total_val = self._add_card(cards_row, "Total Packets")
        self.bytes_val = self._add_card(cards_row, "Data Transferred")
        self.duration_val = self._add_card(cards_row, "Duration")
        outer.addLayout(cards_row)

        self.alerts_card = Card(padding=20)
        alerts_title = QLabel("SECURITY ANALYSIS")
        alerts_title.setObjectName("CardLabel")
        self.alerts_card.addWidget(alerts_title)

        self.no_alerts_label = QLabel("No alerts yet")
        self.no_alerts_label.setStyleSheet("color:#5A5A5E;")
        self.alerts_card.addWidget(self.no_alerts_label)
        self.alert_rows: list[AlertRow] = []

        outer.addWidget(self.alerts_card)
        outer.addStretch()

        self._failed_conns = 0
        self._icmp_count = 0
        self._dns_count = 0
        self._total = 0

    def _add_card(self, layout, label_text) -> QLabel:
        card = Card(padding=18)
        value = QLabel("0")
        value.setObjectName("CardValue")
        caption = QLabel(label_text.upper())
        caption.setObjectName("CardLabel")
        card.addWidget(value)
        card.addWidget(caption)
        layout.addWidget(card)
        return value

    def mark_start(self):
        self.start_time = time.time()

    def on_packet(self, info: dict):
        if self.start_time is None:
            self.mark_start()

        self._total += 1
        proto = info.get("protocol")
        if proto == "ICMP":
            self._icmp_count += 1
        if proto == "DNS":
            self._dns_count += 1
        if proto == "TCP" and "R" in (info.get("flags") or ""):
            self._failed_conns += 1

        self.total_val.setText(f"{self._total:,}")

        if self._total % 25 == 0:
            total_bytes = sum(p.get("length") or 0 for p in self.storage.all_packets())
            self.bytes_val.setText(self._format_bytes(total_bytes))

        elapsed = time.time() - self.start_time
        self.duration_val.setText(self._format_duration(elapsed))

        messages = []
        if self._failed_conns > 20:
            messages.append("High number of failed connections")
        if self._icmp_count > 100:
            messages.append("Large ICMP traffic")
        if self._dns_count > 200:
            messages.append("Unusual DNS request volume")
        self._render_alerts(messages)

    def _render_alerts(self, messages: list[str]):
        if not messages:
            self.no_alerts_label.setVisible(True)
            for row in self.alert_rows:
                row.setVisible(False)
            return

        self.no_alerts_label.setVisible(False)
        for i, msg in enumerate(messages):
            if i < len(self.alert_rows):
                self.alert_rows[i].setVisible(True)
            else:
                row = AlertRow(msg)
                self.alert_rows.append(row)
                self.alerts_card.addWidget(row)

    def reset(self):
        self.start_time = None
        self._failed_conns = self._icmp_count = self._dns_count = self._total = 0
        self.total_val.setText("0")
        self.bytes_val.setText("0")
        self.duration_val.setText("00:00:00")
        self._render_alerts([])

    @staticmethod
    def _format_bytes(n: int) -> str:
        n = float(n)
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"


class ReportsPage(QWidget):
    def __init__(self, storage):
        super().__init__()
        self.setObjectName("RootCanvas")
        self.storage = storage

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 26, 28, 26)
        outer.setSpacing(20)

        title = QLabel("Reports")
        title.setObjectName("SectionTitle")
        outer.addWidget(title)

        card = Card(padding=22)

        desc = QLabel(
            "Export the current capture session as JSON (raw packet data) "
            "or as a summary report — capture time, protocol statistics, "
            "traffic summary, and top connections."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#C8C8CA;")
        card.addWidget(desc)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(self.export_json)
        export_report_btn = QPushButton("Generate Report")
        export_report_btn.setObjectName("Primary")
        export_report_btn.clicked.connect(self.export_report)
        btn_row.addWidget(export_json_btn)
        btn_row.addWidget(export_report_btn)
        btn_row.addStretch()
        card.addLayout(btn_row)

        outer.addWidget(card)
        outer.addStretch()

    def export_json(self):
        os.makedirs("exports", exist_ok=True)
        default_path = os.path.join("exports", "capture.json")
        path, _ = QFileDialog.getSaveFileName(self, "Export JSON", default_path, "JSON Files (*.json)")
        if not path:
            return
        out = self.storage.export_json(path)
        QMessageBox.information(self, "Export Complete", f"Saved to {out}")

    def export_report(self):
        os.makedirs("exports", exist_ok=True)
        default_path = os.path.join("exports", "Network Report.pdf")
        path, _ = QFileDialog.getSaveFileName(self, "Generate Report", default_path, "PDF Files (*.pdf)")
        if not path:
            return
        out = self.storage.export_report(path)
        QMessageBox.information(self, "Report Generated", f"Saved to {out}")
