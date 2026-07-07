"""
main_window.py
The main application window: top menu bar, sidebar navigation, and a
stacked widget holding all pages (Dashboard, Capture, Statistics,
Reports, Settings).
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QTextEdit, QSplitter,
)
from PySide6.QtCore import Qt

from database.storage import Storage
from ui.dashboard import DashboardPage
from ui.packets import PacketsPage
from ui.stats_reports import StatisticsPage, ReportsPage
from ui.settings import SettingsPage
from ui.widgets import Card, PortfolioFooter


PAGES = ["Dashboard", "Capture", "Statistics", "Reports", "Settings"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetScope — Network Packet Analyzer")
        self.resize(1180, 720)

        self.storage = Storage()

        central = QWidget()
        central.setObjectName("RootCanvas")
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        for name in PAGES:
            item = QListWidgetItem(name)
            self.sidebar.addItem(item)
        self.sidebar.currentRowChanged.connect(self._on_nav_changed)

        sidebar_container = QWidget()
        sidebar_container.setObjectName("RootCanvas")
        sidebar_container.setFixedWidth(190)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_layout.addWidget(self.sidebar, 1)
        sidebar_layout.addWidget(PortfolioFooter())

        # --- Pages ---
        self.dashboard_page = DashboardPage()
        self.reports_page = ReportsPage(self.storage)
        self.stats_page = StatisticsPage(self.storage)
        self.settings_page = SettingsPage()
        self.packets_page = PacketsPage(
            self.storage,
            on_packet_callback=self._on_packet,
            on_log=self._on_log,
        )

        self.stack = QStackedWidget()
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.packets_page)
        self.stack.addWidget(self.stats_page)
        self.stack.addWidget(self.reports_page)
        self.stack.addWidget(self.settings_page)

        # --- Right-hand layout: pages + a slim log console at the bottom ---
        right_side = QWidget()
        right_side.setObjectName("RootCanvas")
        right_layout = QVBoxLayout(right_side)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(10)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.stack)

        log_wrapper = QWidget()
        log_wrapper.setObjectName("RootCanvas")
        log_wrapper_layout = QVBoxLayout(log_wrapper)
        log_wrapper_layout.setContentsMargins(28, 0, 28, 20)

        log_card = Card(padding=14)
        log_label = QLabel("LOGS")
        log_label.setObjectName("CardLabel")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(84)
        self.log_text.setStyleSheet(
            "background: transparent; border: none; color: #9A9A9E;"
        )
        log_card.addWidget(log_label)
        log_card.addWidget(self.log_text)
        log_wrapper_layout.addWidget(log_card)

        splitter.addWidget(log_wrapper)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 1)

        right_layout.addWidget(splitter)

        root_layout.addWidget(sidebar_container)
        root_layout.addWidget(right_side, 1)

        self.setCentralWidget(central)
        self.sidebar.setCurrentRow(0)

        self._build_menu()

    def _build_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Export JSON", self.reports_page.export_json)
        file_menu.addAction("Generate Report", self.reports_page.export_report)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        view_menu = menubar.addMenu("View")
        for i, name in enumerate(PAGES):
            view_menu.addAction(name, lambda idx=i: self.sidebar.setCurrentRow(idx))

        settings_menu = menubar.addMenu("Settings")
        settings_menu.addAction("Preferences", lambda: self.sidebar.setCurrentRow(4))

    def _on_nav_changed(self, index: int):
        self.stack.setCurrentIndex(index)

    def _on_packet(self, info: dict):
        self.dashboard_page.on_packet(info)
        self.stats_page.on_packet(info)

    def _on_log(self, message: str):
        import time
        timestamp = time.strftime("%H:%M")
        self.log_text.append(f"{timestamp} {message}")
        if message == "Capture started":
            self.dashboard_page.reset()
            self.stats_page.reset()
            self.stats_page.mark_start()
