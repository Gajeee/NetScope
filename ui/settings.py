"""
settings.py
User Settings page: startup capture toggle, save-folder picker, default
interface, plus an About/Version panel.
"""

import json
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QLineEdit,
)

from capture.sniffer import list_interfaces
from ui.widgets import Card, Divider, PORTFOLIO_URL

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"startup_capture": False, "save_folder": "exports", "default_interface": "Wi-Fi"}


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


class ToggleButton(QPushButton):
    """A compact pill toggle, styled like an iOS settings switch label
    rather than a checkbox."""

    def __init__(self, is_on: bool):
        super().__init__("On" if is_on else "Off")
        self._on = is_on
        self.setFixedWidth(64)
        self._refresh_style()
        self.clicked.connect(self._flip)

    def _flip(self):
        self._on = not self._on
        self.setText("On" if self._on else "Off")
        self._refresh_style()

    def is_on(self) -> bool:
        return self._on

    def _refresh_style(self):
        if self._on:
            self.setObjectName("Primary")
        else:
            self.setObjectName("")
        self.setStyleSheet("")  # let the objectName-based stylesheet re-apply
        self.style().unpolish(self)
        self.style().polish(self)


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("RootCanvas")
        self.config = load_config()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 26, 28, 26)
        outer.setSpacing(20)

        title = QLabel("Settings")
        title.setObjectName("SectionTitle")
        outer.addWidget(title)

        # --- Capture settings card ---
        card = Card(padding=22)

        row1 = QHBoxLayout()
        row1.addWidget(self._row_label("Startup Capture"))
        row1.addStretch()
        self.startup_toggle = ToggleButton(self.config.get("startup_capture", False))
        row1.addWidget(self.startup_toggle)
        card.addLayout(row1)
        card.addWidget(Divider())

        row2 = QHBoxLayout()
        row2.addWidget(self._row_label("Save Captures"))
        row2.addStretch()
        self.folder_edit = QLineEdit(self.config.get("save_folder", "exports"))
        self.folder_edit.setFixedWidth(220)
        row2.addWidget(self.folder_edit)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("Ghost")
        browse_btn.clicked.connect(self._browse_folder)
        row2.addWidget(browse_btn)
        card.addLayout(row2)
        card.addWidget(Divider())

        row3 = QHBoxLayout()
        row3.addWidget(self._row_label("Default Interface"))
        row3.addStretch()
        self.iface_combo = QComboBox()
        self.iface_combo.addItems(list_interfaces() or ["Wi-Fi", "Ethernet"])
        default_iface = self.config.get("default_interface", "Wi-Fi")
        idx = self.iface_combo.findText(default_iface)
        if idx >= 0:
            self.iface_combo.setCurrentIndex(idx)
        row3.addWidget(self.iface_combo)
        card.addLayout(row3)

        save_row = QHBoxLayout()
        save_row.addStretch()
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("Primary")
        save_btn.clicked.connect(self._save)
        save_row.addWidget(save_btn)
        card.addLayout(save_row)

        outer.addWidget(card)

        # --- About card ---
        about_card = Card(padding=22)
        name_label = QLabel("NetScope")
        name_label.setStyleSheet("font-size:16px; font-weight:700;")
        about_card.addWidget(name_label)

        for line in [
            "Version 1.0",
            "Built with Python",
            "Cybersecurity learning project",
            "GitHub — Gajeee/NetScope",
        ]:
            lbl = QLabel(line)
            lbl.setStyleSheet("color:#8A8A8E;")
            about_card.addWidget(lbl)

        about_card.addWidget(Divider())

        copyright_label = QLabel("© 2026 Gajee. All rights reserved.")
        copyright_label.setStyleSheet("color:#5A5A5E; font-size:11px;")
        about_card.addWidget(copyright_label)

        link_label = QLabel(
            f'<a href="{PORTFOLIO_URL}" style="color:#D7D7D9;">{PORTFOLIO_URL}</a>'
        )
        link_label.setOpenExternalLinks(True)
        about_card.addWidget(link_label)

        outer.addWidget(about_card)
        outer.addStretch()

    def _row_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight:500;")
        return lbl

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.folder_edit.setText(folder)

    def _save(self):
        self.config = {
            "startup_capture": self.startup_toggle.is_on(),
            "save_folder": self.folder_edit.text(),
            "default_interface": self.iface_combo.currentText(),
        }
        save_config(self.config)
