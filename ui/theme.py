"""
theme.py
A refined, monochrome, "elevated glass" aesthetic: true-black canvas,
soft charcoal surfaces, hairline borders at low opacity instead of
solid black rules, rounded geometry throughout, and gradient pill
buttons for a tactile, iPhone-settings-like feel — while staying
strictly black / white / grey (no color accents).
"""

BG = "#050505"
SURFACE = "#111113"
SURFACE_RAISED = "#17171A"
BORDER = "rgba(255,255,255,22)"        # soft hairline, not solid black
BORDER_STRONG = "rgba(255,255,255,40)"
TEXT = "#F5F5F5"
TEXT_MUTED = "#8A8A8E"
TEXT_FAINT = "#5A5A5E"

STYLESHEET = f"""
* {{
    outline: none;
}}

QWidget {{
    color: {TEXT};
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
    font-weight: bold;
    font-size: 13px;
}}

QLabel, QCheckBox, QRadioButton {{
    background: transparent;
}}

QMainWindow, QDialog {{
    background-color: {BG};
}}

#RootCanvas {{
    background-color: {BG};
}}

QMenuBar {{
    background-color: {BG};
    color: {TEXT_MUTED};
    border-bottom: 1px solid {BORDER};
    padding: 4px 6px;
}}
QMenuBar::item {{
    padding: 6px 12px;
    border-radius: 6px;
    background: transparent;
}}
QMenuBar::item:selected {{
    background-color: {SURFACE_RAISED};
    color: {TEXT};
}}
QMenu {{
    background-color: {SURFACE_RAISED};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
}}
QMenu::item {{
    padding: 7px 16px;
    border-radius: 6px;
}}
QMenu::item:selected {{
    background-color: rgba(255,255,255,16);
}}

/* ---------- Sidebar ---------- */
QListWidget#Sidebar {{
    background-color: {BG};
    border: none;
    border-right: 1px solid {BORDER};
    padding: 18px 10px;
    outline: 0;
}}
QListWidget#Sidebar::item {{
    padding: 11px 16px;
    margin: 2px 2px;
    border-radius: 10px;
    color: {TEXT_MUTED};
    font-weight: 500;
}}
QListWidget#Sidebar::item:selected {{
    color: {TEXT};
    background-color: {SURFACE_RAISED};
}}
QListWidget#Sidebar::item:hover:!selected {{
    color: {TEXT};
    background-color: rgba(255,255,255,6);
}}

/* ---------- Elevated cards (see widgets.Card, shadow via QGraphicsDropShadowEffect) ---------- */
QFrame#Card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 16px;
}}

QLabel#CardValue {{
    font-size: 28px;
    font-weight: 600;
    color: {TEXT};
    letter-spacing: -0.5px;
}}
QLabel#CardLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
}}
QLabel#SectionTitle {{
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: {TEXT};
}}

/* ---------- Buttons ---------- */
QPushButton {{
    background-color: {SURFACE_RAISED};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 9px 20px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: rgba(255,255,255,14);
    border: 1px solid {BORDER_STRONG};
}}
QPushButton:pressed {{
    background-color: rgba(255,255,255,6);
}}
QPushButton:disabled {{
    color: {TEXT_FAINT};
    border: 1px solid rgba(255,255,255,10);
    background-color: transparent;
}}

QPushButton#Primary {{
    background-color: {TEXT};
    color: #050505;
    border: none;
    font-weight: 600;
}}
QPushButton#Primary:hover {{
    background-color: #E2E2E2;
}}
QPushButton#Primary:pressed {{
    background-color: #C9C9C9;
}}
QPushButton#Primary:disabled {{
    background-color: rgba(255,255,255,20);
    color: rgba(5,5,5,120);
}}

QPushButton#Danger {{
    border: 1px solid rgba(240,85,90,120);
    color: #F0555A;
    background-color: rgba(240,85,90,14);
}}
QPushButton#Danger:hover {{
    background-color: rgba(240,85,90,28);
}}
QPushButton#Danger:disabled {{
    border: 1px solid rgba(255,255,255,10);
    color: {TEXT_FAINT};
    background-color: transparent;
}}

QPushButton#Ghost {{
    background-color: transparent;
    border: 1px solid transparent;
    color: {TEXT_MUTED};
}}
QPushButton#Ghost:hover {{
    color: {TEXT};
    background-color: rgba(255,255,255,8);
}}

/* ---------- Inputs ---------- */
QLineEdit, QComboBox {{
    background-color: {SURFACE_RAISED};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 9px 14px;
    color: {TEXT};
    selection-background-color: rgba(255,255,255,40);
}}
QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {BORDER_STRONG};
    background-color: #1B1B1E;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE_RAISED};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    selection-background-color: rgba(255,255,255,16);
    padding: 4px;
    outline: none;
}}

/* ---------- Table ---------- */
QTableWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    gridline-color: transparent;
    selection-background-color: rgba(255,255,255,14);
    selection-color: {TEXT};
    padding: 2px;
}}
QTableWidget::item {{
    border: none;
    padding: 6px 4px;
    border-bottom: 1px solid rgba(255,255,255,8);
}}
QHeaderView {{
    background-color: transparent;
    border: none;
}}
QHeaderView::section {{
    background-color: transparent;
    color: {TEXT_MUTED};
    padding: 10px 6px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-size: 11px;
    font-weight: 600;
}}
QTableCornerButton::section {{
    background-color: transparent;
    border: none;
}}

/* ---------- Text edit (logs / details) ---------- */
QTextEdit {{
    background-color: {SURFACE_RAISED};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 10px;
    color: {TEXT};
}}

/* ---------- Scrollbar ---------- */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255,255,255,26);
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(255,255,255,44);
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: rgba(255,255,255,26);
    border-radius: 5px;
    min-width: 24px;
}}

/* ---------- Splitter ---------- */
QSplitter::handle {{
    background-color: transparent;
}}
QSplitter::handle:horizontal {{
    width: 18px;
}}
QSplitter::handle:vertical {{
    height: 10px;
}}

/* ---------- Tabs (unused currently, kept for consistency) ---------- */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QTabBar::tab {{
    background: transparent;
    color: {TEXT_MUTED};
    padding: 8px 16px;
    border: none;
}}
QTabBar::tab:selected {{
    color: {TEXT};
}}
"""
