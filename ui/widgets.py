"""
widgets.py
Small reusable, custom-painted UI primitives used across NetScope.

Nothing here uses emoji glyphs. Status indicators, bars, and icons are
drawn with QPainter or built from styled Qt shapes so they render
identically everywhere and stay in the monochrome palette.
"""

from PySide6.QtWidgets import QWidget, QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QLabel
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient
from PySide6.QtCore import Qt, QRectF


ACCENT = QColor("#F2F2F2")
MUTED = QColor("#6B6B6E")
SUCCESS = QColor("#3ED598")
WARNING = QColor("#F2A93B")
DANGER = QColor("#F0555A")


def elevate(widget: QWidget, blur: int = 28, y_offset: int = 10, alpha: int = 140):
    """Apply a soft drop shadow so panels read as lifted, glassy surfaces
    rather than flat rectangles with a hard border."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)
    return effect


class Card(QFrame):
    """An elevated, rounded surface. Use as the base container for any
    grouped content instead of a bordered QFrame."""

    def __init__(self, parent=None, padding=20):
        super().__init__(parent)
        self.setObjectName("Card")
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(padding, padding, padding, padding)
        self.layout_.setSpacing(10)
        elevate(self, blur=32, y_offset=8, alpha=110)

    def addWidget(self, w):
        self.layout_.addWidget(w)

    def addLayout(self, l):
        self.layout_.addLayout(l)


class StatusDot(QWidget):
    """A small filled circle used instead of a text bullet like '●'."""

    def __init__(self, color: QColor = MUTED, diameter: int = 9, glow: bool = False):
        super().__init__()
        self._color = color
        self._diameter = diameter
        self._glow = glow
        self.setFixedSize(diameter + 8, diameter + 8)

    def set_color(self, color: QColor, glow: bool = False):
        self._color = color
        self._glow = glow
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(
            (self.width() - self._diameter) / 2,
            (self.height() - self._diameter) / 2,
            self._diameter,
            self._diameter,
        )
        if self._glow:
            glow_color = QColor(self._color)
            glow_color.setAlpha(70)
            painter.setBrush(glow_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(rect.adjusted(-4, -4, 4, 4))

        painter.setBrush(self._color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)
        painter.end()


class StatusIndicator(QWidget):
    """Dot + label combo, e.g. a small circle followed by 'Ready'."""

    def __init__(self, text: str = "Ready", color: QColor = MUTED):
        super().__init__()
        from PySide6.QtWidgets import QHBoxLayout

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.dot = StatusDot(color)
        self.label = QLabel(text)
        self.label.setStyleSheet("color: #E7E7E7; font-weight: 500;")

        layout.addWidget(self.dot)
        layout.addWidget(self.label)
        layout.addStretch()

    def set_state(self, text: str, color: QColor, glow: bool = False):
        self.label.setText(text)
        self.dot.set_color(color, glow)


class MeterBar(QWidget):
    """A smooth, rounded, gradient-filled horizontal meter — replaces
    ASCII block characters ('████') for protocol-usage rows."""

    def __init__(self, height: int = 8):
        super().__init__()
        self._ratio = 0.0
        self.setFixedHeight(height)

    def set_ratio(self, ratio: float):
        self._ratio = max(0.0, min(1.0, ratio))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_rect = QRectF(0, 0, self.width(), self.height())
        radius = self.height() / 2

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 18))
        painter.drawRoundedRect(track_rect, radius, radius)

        if self._ratio > 0:
            fill_width = max(self.height(), self._ratio * self.width())
            fill_rect = QRectF(0, 0, fill_width, self.height())
            gradient = QLinearGradient(0, 0, fill_width, 0)
            gradient.setColorAt(0.0, QColor("#CFCFCF"))
            gradient.setColorAt(1.0, QColor("#FFFFFF"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(fill_rect, radius, radius)

        painter.end()


class Divider(QFrame):
    """A near-invisible 1px hairline, softer than a hard black border."""

    def __init__(self, vertical: bool = False):
        super().__init__()
        self.setFrameShape(QFrame.VLine if vertical else QFrame.HLine)
        self.setStyleSheet("background-color: rgba(255,255,255,14); max-height:1px; border: none;")
        self.setFixedHeight(1) if not vertical else None


PORTFOLIO_URL = "https://gajeee.github.io/Portfolio/"


class PortfolioFooter(QWidget):
    """Small persistent footer: copyright line + a clickable link to the
    author's portfolio. Used at the bottom of the sidebar."""

    def __init__(self, align: Qt.AlignmentFlag = Qt.AlignLeft):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 16)
        layout.setSpacing(4)

        copyright_label = QLabel("© 2026 Gajee. All rights reserved.")
        copyright_label.setWordWrap(True)
        copyright_label.setStyleSheet("color:#5A5A5E; font-size:10px; font-weight:600;")
        copyright_label.setAlignment(align)

        link_label = QLabel(f'<a href="{PORTFOLIO_URL}" style="color:#B9B9BC; text-decoration:none;">Portfolio</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet("font-size:11px; font-weight:700;")
        link_label.setAlignment(align)

        layout.addWidget(copyright_label)
        layout.addWidget(link_label)
