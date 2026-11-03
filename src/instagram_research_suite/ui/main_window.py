"""Main dark-themed window inspired by the approved Instagram Research Suite mockup."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
    QScrollArea, QStackedWidget, QVBoxLayout, QWidget,
)

from instagram_research_suite.storage.database import Database
from instagram_research_suite.ui.pages import DashboardPage, FeaturePage, FollowersPage


APP_STYLE = """
QWidget { background: #080f25; color: #edf2ff; font-family: 'Segoe UI'; font-size: 10pt; }
QMainWindow { background: #080f25; }
QFrame#Sidebar { background: #0b142b; border-right: 1px solid #26345c; }
QLabel#Brand { color: white; font-size: 17pt; font-weight: 700; padding: 8px 4px 18px; }
QPushButton#NavButton { text-align: left; padding: 11px 13px; border: 0; border-radius: 8px; color: #aab8d8; }
QPushButton#NavButton:hover { background: #18264b; color: white; }
QPushButton#NavButton:checked { background: #5636d9; color: white; font-weight: 600; }
QLabel#PageTitle { font-size: 21pt; font-weight: 700; color: white; }
QLabel#Muted { color: #93a4c8; }
QFrame#Card { background: #101b37; border: 1px solid #263762; border-radius: 12px; }
QPushButton { background: #5636d9; border: 0; border-radius: 8px; padding: 9px 13px; color: white; font-weight: 600; }
QPushButton:hover { background: #704ff2; }
QLineEdit, QComboBox { background: #0a142d; border: 1px solid #30416c; border-radius: 7px; padding: 9px; color: white; }
QTableWidget { background: #0c1731; alternate-background-color: #101e3d; gridline-color: #24365f; border: 1px solid #263762; border-radius: 8px; }
QHeaderView::section { background: #17264a; color: #b9c8e9; padding: 8px; border: 0; }
"""


class MainWindow(QMainWindow):
    """Application shell containing navigation and the feature page stack."""

    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self.setWindowTitle("Instagram Research Suite")
        self.resize(1500, 920)
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(APP_STYLE)
        self._build_layout()

    def _build_layout(self) -> None:
        """Create the fixed sidebar and switchable content area."""
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(235)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 18, 14, 16)
        brand = QLabel("◎  Instagram\n     Research Suite")
        brand.setObjectName("Brand")
        side_layout.addWidget(brand)

        self.stack = QStackedWidget()
        self.pages: dict[str, QWidget] = {}
        self.nav_buttons: list[QPushButton] = []
        navigation = [
            ("Dashboard", DashboardPage()),
            ("Profile Analysis", FeaturePage("Profile Analysis", "Explore profile details available from permitted sources.")),
            ("Followers & Following", FollowersPage(self.database)),
            ("Posts & Engagement", FeaturePage("Posts & Engagement", "Review accessible media, comments and engagement metrics.")),
            ("Mentions & Tags", FeaturePage("Mentions & Tags", "Review mentions and tags surfaced through authorised integrations.")),
            ("Stories & Highlights", FeaturePage("Stories & Highlights", "Browse stories and highlights only when a supported source permits access.")),
            ("Account Insights", FeaturePage("Account Insights", "View account type, visibility and authorised aggregate insights.")),
            ("Snapshots", FeaturePage("Snapshots", "Review locally saved historical research snapshots.")),
            ("Compare Profiles", FeaturePage("Compare Profiles", "Compare collected profile and engagement information.")),
            ("Export Center", FeaturePage("Export Center", "Export your locally collected research data.")),
            ("Settings", FeaturePage("Settings", "Configure appearance, data storage and provider settings.")),
        ]

        for index, (name, page) in enumerate(navigation):
            self.pages[name] = page
            self.stack.addWidget(page)
            button = QPushButton(name)
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self._select_page(i))
            side_layout.addWidget(button)
            self.nav_buttons.append(button)

        side_layout.addStretch(1)
        account_label = QLabel("●  Local workspace\n     Demo / authorised data")
        account_label.setObjectName("Muted")
        side_layout.addWidget(account_label)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 16, 18, 18)
        content_layout.addWidget(self.stack)
        layout.addWidget(sidebar)
        layout.addWidget(content, 1)
        self.setCentralWidget(root)
        self._select_page(0)

    def _select_page(self, index: int) -> None:
        """Switch pages and keep exactly one sidebar item selected."""
        self.stack.setCurrentIndex(index)
        for button_index, button in enumerate(self.nav_buttons):
            button.setChecked(button_index == index)
