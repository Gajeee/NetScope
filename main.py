"""
main.py
NetScope entry point.

Shows a brief startup/loading screen (checking adapters, loading the
database, preparing the UI) and then opens the main window.

Run with:
    python main.py

Packet capture requires elevated privileges:
    Windows : run as Administrator, with Npcap installed (https://npcap.com)
    macOS   : sudo python main.py   (or grant permission when prompted)
    Linux   : sudo python main.py   (or set a capability: 
              sudo setcap cap_net_raw,cap_net_admin=eip $(which python3))
"""

import sys

from PySide6.QtWidgets import QApplication, QSplashScreen, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont

from ui.theme import STYLESHEET
from ui.main_window import MainWindow


def make_splash_pixmap() -> QPixmap:
    width, height = 440, 280
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#050505"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Soft rounded card behind the content, matching the app's elevated-card look
    card_rect = pixmap.rect().adjusted(24, 24, -24, -24)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(17, 17, 19))
    painter.drawRoundedRect(card_rect, 20, 20)
    painter.setPen(QColor(255, 255, 255, 22))
    painter.drawRoundedRect(card_rect, 20, 20)

    title_font = QFont("Helvetica", 22, QFont.Bold)
    painter.setFont(title_font)
    painter.setPen(QColor("#F5F5F5"))
    painter.drawText(pixmap.rect().adjusted(0, 50, 0, 0), Qt.AlignHCenter | Qt.AlignTop, "NetScope")

    sub_font = QFont("Helvetica", 10)
    painter.setFont(sub_font)
    painter.setPen(QColor("#8A8A8E"))
    painter.drawText(
        pixmap.rect().adjusted(0, 88, 0, 0), Qt.AlignHCenter | Qt.AlignTop, "Initializing"
    )

    lines = [
        "Network adapters found",
        "Database loaded",
        "Interface ready",
    ]
    item_font = QFont("Helvetica", 10)
    painter.setFont(item_font)
    y = 138
    dot_x = width / 2 - 78
    for line in lines:
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#3ED598"))
        painter.drawEllipse(int(dot_x), y + 5, 7, 7)
        painter.setPen(QColor("#D7D7D9"))
        painter.drawText(int(dot_x) + 16, y + 12, line)
        y += 26

    painter.end()
    return pixmap


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    splash_pix = make_splash_pixmap()
    splash = QSplashScreen(splash_pix)
    splash.show()
    app.processEvents()

    window_holder = {}

    def finish_startup():
        window = MainWindow()
        window_holder["window"] = window
        window.show()
        splash.finish(window)

    QTimer.singleShot(1200, finish_startup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
