"""Reusable dashboard, feature placeholder and follower snapshot screens."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from instagram_research_suite.providers.demo import DemoProvider
from instagram_research_suite.storage.database import Database


def make_card(title: str, value: str, note: str) -> QFrame:
    """Build a consistent metric card for the dashboard."""
    card = QFrame()
    card.setObjectName("Card")
    layout = QVBoxLayout(card)
    heading = QLabel(title)
    heading.setStyleSheet("color:#9fb0d4; font-size:9pt;")
    metric = QLabel(value)
    metric.setStyleSheet("font-size:23pt; font-weight:700; color:white;")
    detail = QLabel(note)
    detail.setStyleSheet("color:#22d3a6; font-size:9pt;")
    layout.addWidget(heading)
    layout.addWidget(metric)
    layout.addWidget(detail)
    return card


class DashboardPage(QWidget):
    """Overview page with high-level metrics and quick navigation cues."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Welcome back!")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Your local Instagram research workspace at a glance.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        metrics = QGridLayout()
        metrics.setSpacing(12)
        metrics.addWidget(make_card("Total Followers", "12,458", "Demo preview data"), 0, 0)
        metrics.addWidget(make_card("Following", "587", "Demo preview data"), 0, 1)
        metrics.addWidget(make_card("Posts", "342", "Illustrative only"), 0, 2)
        metrics.addWidget(make_card("Engagement Rate", "4.8%", "Illustrative only"), 0, 3)
        layout.addLayout(metrics)

        lower = QGridLayout()
        lower.setSpacing(12)
        lower.addWidget(self._info_card("Engagement Overview", "Connect an authorised provider or import your own data to populate analytics."), 0, 0)
        lower.addWidget(self._info_card("Account Classification", "Public/private and professional account labels appear only when a source provides them."), 0, 1)
        lower.addWidget(self._info_card("Recent Activity", "No live activity is being monitored. Historical events will appear after data collection."), 1, 0)
        lower.addWidget(self._info_card("Quick Actions", "Open Followers & Following to import a list and save your first snapshot."), 1, 1)
        layout.addLayout(lower)
        layout.addStretch(1)

    @staticmethod
    def _info_card(title: str, description: str) -> QFrame:
        """Create a simple information panel with a title and explanatory copy."""
        card = QFrame()
        card.setObjectName("Card")
        box = QVBoxLayout(card)
        heading = QLabel(title)
        heading.setStyleSheet("font-size:13pt; font-weight:700;")
        body = QLabel(description)
        body.setWordWrap(True)
        body.setStyleSheet("color:#9fb0d4;")
        box.addWidget(heading)
        box.addWidget(body)
        box.addStretch(1)
        card.setMinimumHeight(145)
        return card


class FeaturePage(QWidget):
    """Honest placeholder for modules that will be implemented in later milestones."""

    def __init__(self, title_text: str, description: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel(title_text)
        title.setObjectName("PageTitle")
        description_label = QLabel(description)
        description_label.setObjectName("Muted")
        description_label.setWordWrap(True)
        panel = QFrame()
        panel.setObjectName("Card")
        panel_layout = QVBoxLayout(panel)
        status = QLabel("MODULE FOUNDATION READY")
        status.setStyleSheet("color:#a78bfa; font-weight:700; letter-spacing:1px;")
        detail = QLabel("This screen is scaffolded. A live data connector and its permissions must be configured before it can display account data.")
        detail.setWordWrap(True)
        detail.setStyleSheet("color:#aab8d8;")
        panel_layout.addWidget(status)
        panel_layout.addWidget(detail)
        panel_layout.addStretch(1)
        panel.setMinimumHeight(220)
        layout.addWidget(title)
        layout.addWidget(description_label)
        layout.addSpacing(12)
        layout.addWidget(panel)
        layout.addStretch(1)


class FollowersPage(QWidget):
    """Follower/following list viewer with import-ready demo and local snapshots."""

    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self.provider = DemoProvider()
        self.active_list = "followers"
        self.records: list[dict[str, str | bool]] = []
        layout = QVBoxLayout(self)

        title = QLabel("Followers & Following")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Load permitted data, inspect every retrieved row, and save dated snapshots.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        controls = QHBoxLayout()
        self.handle_input = QLineEdit()
        self.handle_input.setPlaceholderText("Instagram username (without @)")
        self.followers_button = QPushButton("Followers")
        self.following_button = QPushButton("Following")
        self.load_button = QPushButton("Load demo preview")
        self.snapshot_button = QPushButton("Save snapshot")
        self.followers_button.clicked.connect(lambda: self._set_list("followers"))
        self.following_button.clicked.connect(lambda: self._set_list("following"))
        self.load_button.clicked.connect(self._load_demo)
        self.snapshot_button.clicked.connect(self._save_snapshot)
        controls.addWidget(self.handle_input, 2)
        controls.addWidget(self.followers_button)
        controls.addWidget(self.following_button)
        controls.addWidget(self.load_button)
        controls.addWidget(self.snapshot_button)
        layout.addLayout(controls)

        self.status_label = QLabel("No list loaded. Demo records are fictional and clearly labelled.")
        self.status_label.setObjectName("Muted")
        layout.addWidget(self.status_label)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["#", "Username", "Display name", "Visibility"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)
        self._set_list("followers")

    def _set_list(self, list_type: str) -> None:
        """Change the selected relationship list and update button states."""
        self.active_list = list_type
        self.followers_button.setChecked(list_type == "followers")
        self.following_button.setChecked(list_type == "following")
        self.followers_button.setStyleSheet("background:#704ff2;" if list_type == "followers" else "")
        self.following_button.setStyleSheet("background:#704ff2;" if list_type == "following" else "")

    def _load_demo(self) -> None:
        """Populate a tiny fictional fixture without contacting Instagram."""
        handle = self.handle_input.text().strip() or "sample_account"
        result = self.provider.fetch_relationships(handle, self.active_list)
        self.records = result.records
        self.table.setRowCount(len(self.records))
        for row_index, record in enumerate(self.records):
            values = [
                str(row_index + 1), str(record["username"]), str(record["display_name"]),
                "Private" if record["is_private"] else "Public",
            ]
            for column, value in enumerate(values):
                self.table.setItem(row_index, column, QTableWidgetItem(value))
        self.status_label.setText(
            f"{len(self.records)} demo rows loaded · completeness: {result.completeness} · {result.message}"
        )

    def _save_snapshot(self) -> None:
        """Save the currently displayed rows and preserve their uncertain completeness."""
        if not self.records:
            QMessageBox.information(self, "Nothing to save", "Load or import a list before saving a snapshot.")
            return
        handle = self.handle_input.text().strip() or "sample_account"
        snapshot_id = self.database.save_snapshot(
            account_handle=handle,
            list_type=self.active_list,
            records=self.records,
            source=self.provider.name,
            completeness="unknown",
        )
        QMessageBox.information(self, "Snapshot saved", f"Local snapshot #{snapshot_id} saved successfully.")
