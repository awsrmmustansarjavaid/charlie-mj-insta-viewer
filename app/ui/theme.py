"""Centralised premium dark theme and reusable stylesheet."""

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background: #0B1020;
    color: #E7ECF7;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QWidget#Sidebar {
    background: #0D1425;
    border-right: 1px solid #24304B;
}
QLabel#Brand {
    color: #FFFFFF;
    font-size: 16pt;
    font-weight: 700;
}
QLabel#Muted { color: #93A4C2; }
QLabel#PageTitle {
    color: #FFFFFF;
    font-size: 20pt;
    font-weight: 700;
}
QFrame#Panel, QFrame#MetricCard {
    background: #111A2E;
    border: 1px solid #263653;
    border-radius: 12px;
}
QLabel#MetricValue {
    color: #FFFFFF;
    font-size: 22pt;
    font-weight: 700;
}
QPushButton {
    background: #202D49;
    color: #EAF0FF;
    border: 1px solid #344565;
    border-radius: 8px;
    padding: 9px 13px;
}
QPushButton:hover { background: #2C3C60; border-color: #8B5CF6; }
QPushButton#PrimaryButton {
    background: #713CEB;
    border: 1px solid #966BFF;
    font-weight: 600;
}
QPushButton#PrimaryButton:hover { background: #8655F4; }
QPushButton#NavButton {
    text-align: left;
    padding: 10px 12px;
    background: transparent;
    border: none;
    color: #B7C3DA;
}
QPushButton#NavButton:checked {
    background: #39228C;
    color: #FFFFFF;
    border-left: 3px solid #A78BFA;
}
QLineEdit, QComboBox, QTableWidget, QTextEdit {
    background: #0D172B;
    color: #E7ECF7;
    border: 1px solid #2A3A59;
    border-radius: 7px;
    padding: 7px;
    selection-background-color: #713CEB;
}
QHeaderView::section {
    background: #17243B;
    color: #AFC0DF;
    border: none;
    padding: 8px;
    font-weight: 600;
}
QTableWidget { gridline-color: #25334D; }
QScrollBar:vertical { background: #0B1020; width: 10px; }
QScrollBar::handle:vertical { background: #354568; border-radius: 5px; }
QTabWidget::pane { border: 1px solid #263653; border-radius: 8px; }
QTabBar::tab { background: #111A2E; padding: 9px 14px; }
QTabBar::tab:selected { background: #39228C; }
"""
