"""Main desktop window and page composition."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from app.data.database import Database
from app.services.analytics import classify_accounts, compare_usernames, emoji_counts
from app.services.provider import Account, Comment, DemoProvider, RetrievalStatus
from app.ui.theme import DARK_STYLESHEET


class MainWindow(QMainWindow):
    """Primary window: navigation, dashboard, browsing, research and exports."""

    NAV_ITEMS = [
        "Dashboard",
        "Instagram Style View",
        "Profile Analysis",
        "Followers & Following",
        "Posts & Engagement",
        "Mentions & Tags",
        "Stories & Highlights",
        "Account Insights",
        "Snapshots",
        "Compare Profiles",
        "Export Center",
        "Settings",
    ]

    def __init__(self, database: Database, data_dir: Path):
        """Build the window and load the local demo provider."""
        super().__init__()
        self.database = database
        self.data_dir = data_dir
        self.provider = DemoProvider()
        self.profile = "demo_profile"
        self.current_accounts: list[Account] = []
        self.current_status: RetrievalStatus | None = None
        self.current_list_type = "Followers"

        self.setWindowTitle("Instagram Research Suite")
        self.resize(1500, 920)
        self.setMinimumSize(1180, 760)
        self.setStyleSheet(DARK_STYLESHEET)

        central = QWidget()
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_sidebar())
        root_layout.addWidget(self._build_content(), 1)
        self.setCentralWidget(central)
        self._show_page(0)

    def _build_sidebar(self) -> QWidget:
        """Create the persistent left navigation rail."""
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(225)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 20, 14, 16)
        layout.setSpacing(7)

        brand = QLabel("◎  Instagram\n     Research Suite")
        brand.setObjectName("Brand")
        layout.addWidget(brand)
        tagline = QLabel("ANALYZE  •  EXPLORE  •  TRACK")
        tagline.setObjectName("Muted")
        layout.addWidget(tagline)
        layout.addSpacing(16)

        self.nav_buttons: list[QPushButton] = []
        for index, item in enumerate(self.NAV_ITEMS):
            button = QPushButton(item)
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, page=index: self._show_page(page))
            layout.addWidget(button)
            self.nav_buttons.append(button)

        layout.addStretch()
        account = QLabel("●  Demo Workspace\n    Local sample data")
        account.setObjectName("Muted")
        layout.addWidget(account)
        return sidebar

    def _build_content(self) -> QWidget:
        """Create the stacked page area and its top-level header."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Instagram Research Suite")
        title.setObjectName("PageTitle")
        header.addWidget(title)
        header.addStretch()
        self.provider_badge = QLabel("● LOCAL DEMO DATA")
        self.provider_badge.setObjectName("Muted")
        header.addWidget(self.provider_badge)
        layout.addLayout(header)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._dashboard_page())
        self.pages.addWidget(self._instagram_page())
        self.pages.addWidget(self._profile_page())
        self.pages.addWidget(self._followers_page())
        self.pages.addWidget(self._engagement_page())
        self.pages.addWidget(self._mentions_page())
        self.pages.addWidget(self._stories_page())
        self.pages.addWidget(self._insights_page())
        self.pages.addWidget(self._snapshots_page())
        self.pages.addWidget(self._compare_page())
        self.pages.addWidget(self._export_page())
        self.pages.addWidget(self._settings_page())
        layout.addWidget(self.pages, 1)
        return container

    def _panel(self, title: str, subtitle: str = "") -> tuple[QFrame, QVBoxLayout]:
        """Create a standard bordered card panel."""
        frame = QFrame()
        frame.setObjectName("Panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 16)
        heading = QLabel(title)
        heading.setStyleSheet("font-size: 12pt; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(heading)
        if subtitle:
            note = QLabel(subtitle)
            note.setObjectName("Muted")
            layout.addWidget(note)
        return frame, layout

    def _metric_card(self, title: str, value: str, delta: str) -> QFrame:
        """Create a compact KPI card for dashboard summaries."""
        card = QFrame()
        card.setObjectName("MetricCard")
        layout = QVBoxLayout(card)
        label = QLabel(title)
        label.setObjectName("Muted")
        number = QLabel(value)
        number.setObjectName("MetricValue")
        change = QLabel(delta)
        change.setStyleSheet("color: #34D399;")
        layout.addWidget(label)
        layout.addWidget(number)
        layout.addWidget(change)
        return card

    def _dashboard_page(self) -> QWidget:
        """Create the dashboard overview with metrics and quick actions."""
        page = QWidget()
        layout = QVBoxLayout(page)
        welcome = QLabel("Welcome back, Researcher")
        welcome.setStyleSheet("font-size: 17pt; font-weight: 700;")
        layout.addWidget(welcome)
        note = QLabel("Your workspace overview. Counts below are illustrative demo values.")
        note.setObjectName("Muted")
        layout.addWidget(note)

        metrics = QHBoxLayout()
        for title, value, delta in [
            ("Total Followers", "12,458", "Demo metric"),
            ("Following", "587", "Demo metric"),
            ("Posts", "342", "Demo metric"),
            ("Engagement Rate", "4.8%", "Demo metric"),
        ]:
            metrics.addWidget(self._metric_card(title, value, delta))
        layout.addLayout(metrics)

        lower = QHBoxLayout()
        overview, overview_layout = self._panel("Research Overview", "Modules available in this local starter release")
        for text in [
            "• Profile and Instagram-style content viewer",
            "• Follower/following retrieval with completeness status",
            "• Immutable local snapshots and comparisons",
            "• Account category and visibility breakdown",
            "• Comments, replies and visible emoji analysis",
            "• Mentions, stories and highlights workspace",
        ]:
            label = QLabel(text)
            label.setObjectName("Muted")
            overview_layout.addWidget(label)
        lower.addWidget(overview, 2)

        actions, actions_layout = self._panel("Quick Actions")
        for label, target in [
            ("View Followers", 3),
            ("Open Instagram Style View", 1),
            ("Analyze Account Types", 7),
            ("View Snapshot History", 8),
        ]:
            button = QPushButton(label)
            button.setObjectName("PrimaryButton")
            button.clicked.connect(lambda checked=False, page=target: self._show_page(page))
            actions_layout.addWidget(button)
        lower.addWidget(actions, 1)
        layout.addLayout(lower, 1)
        return page

    def _instagram_page(self) -> QWidget:
        """Create an Instagram-inspired browsing canvas using sample media cards."""
        page = QWidget()
        layout = QHBoxLayout(page)
        feed, feed_layout = self._panel("Home Feed", "Instagram-inspired demo browsing experience")
        stories = QHBoxLayout()
        for name in ["Your Story", "travel_diary", "sarah", "foodie", "nature"]:
            tile = QLabel(f"◉\n{name}")
            tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tile.setMinimumWidth(85)
            tile.setStyleSheet(
                "background:#202D49;border:2px solid #8B5CF6;border-radius:12px;padding:12px;"
            )
            stories.addWidget(tile)
        feed_layout.addLayout(stories)

        post = QFrame()
        post.setObjectName("MetricCard")
        post_layout = QVBoxLayout(post)
        post_layout.addWidget(QLabel("travel_diary  •  Demo post"))
        media = QLabel("PHOTO / REEL PREVIEW")
        media.setAlignment(Qt.AlignmentFlag.AlignCenter)
        media.setMinimumHeight(300)
        media.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #173A5E,stop:1 #643B94);"
            "border-radius:10px;font-size:18pt;font-weight:700;"
        )
        post_layout.addWidget(media)
        post_layout.addWidget(QLabel("♡  12.4K     ◯  342 comments     ↗  Share"))
        post_layout.addWidget(QLabel("Sunset vibes 🌅  #travel #nature"))
        feed_layout.addWidget(post)
        layout.addWidget(feed, 3)

        side, side_layout = self._panel("Suggested for you")
        for user in ["foodie.life", "nature_lovers", "urban.views", "minimal.style"]:
            side_layout.addWidget(QLabel(f"◉  {user}       Follow"))
        side_layout.addStretch()
        layout.addWidget(side, 1)
        return page

    def _profile_page(self) -> QWidget:
        """Create a profile overview with highlights and a post grid placeholder."""
        page = QWidget()
        layout = QVBoxLayout(page)
        profile, profile_layout = self._panel("Profile Explorer", "Profile details depend on the selected provider.")
        profile_layout.addWidget(QLabel("◉  travel_diary       Public demo profile"))
        profile_layout.addWidget(QLabel("342 Posts      48.7K Followers      587 Following"))
        profile_layout.addWidget(QLabel("Exploring the world one place at a time • Travel / Photography"))
        profile_layout.addWidget(QLabel("Highlights:  Bali  •  Japan  •  Europe  •  Food  •  Nature"))
        layout.addWidget(profile)
        grid, grid_layout = self._panel("Posts / Reels / Tagged")
        grid_layout.addWidget(QLabel("Select Instagram Style View to explore the sample feed."))
        layout.addWidget(grid, 1)
        return page

    def _followers_page(self) -> QWidget:
        """Build the follower/following explorer with snapshot controls."""
        page = QWidget()
        layout = QVBoxLayout(page)
        panel, panel_layout = self._panel(
            "Followers & Following Explorer",
            "Complete means complete for the selected provider response—not necessarily complete for Instagram."
        )
        controls = QHBoxLayout()
        self.list_selector = QComboBox()
        self.list_selector.addItems(["Followers", "Following"])
        self.list_selector.currentTextChanged.connect(self._load_accounts)
        self.account_search = QLineEdit()
        self.account_search.setPlaceholderText("Search username or display name...")
        self.account_search.textChanged.connect(self._filter_accounts)
        load_button = QPushButton("Load List")
        load_button.setObjectName("PrimaryButton")
        load_button.clicked.connect(self._load_accounts)
        snapshot_button = QPushButton("Take Snapshot")
        snapshot_button.clicked.connect(self._take_snapshot)
        export_button = QPushButton("Export CSV")
        export_button.clicked.connect(self._export_accounts)
        controls.addWidget(self.list_selector)
        controls.addWidget(self.account_search, 1)
        controls.addWidget(load_button)
        controls.addWidget(snapshot_button)
        controls.addWidget(export_button)
        panel_layout.addLayout(controls)

        self.completeness_label = QLabel("Load a list to see retrieval and completeness information.")
        self.completeness_label.setObjectName("Muted")
        panel_layout.addWidget(self.completeness_label)

        self.account_table = QTableWidget(0, 6)
        self.account_table.setHorizontalHeaderLabels(
            ["#", "Profile", "Username", "Account Type", "Visibility", "Verified"]
        )
        self.account_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.account_table.setAlternatingRowColors(True)
        panel_layout.addWidget(self.account_table, 1)
        layout.addWidget(panel)
        return page

    def _engagement_page(self) -> QWidget:
        """Create a post engagement and comment/emoji analysis screen."""
        page = QWidget()
        layout = QHBoxLayout(page)
        post, post_layout = self._panel("Post Engagement Explorer", "Example content; real results depend on provider access.")
        post_layout.addWidget(QLabel("travel_diary  •  Sunset vibes 🌅"))
        image = QLabel("POST MEDIA PREVIEW")
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setMinimumHeight(300)
        image.setStyleSheet("background:#263B5D;border-radius:10px;font-size:18pt;")
        post_layout.addWidget(image)
        post_layout.addWidget(QLabel("♡ 12.4K likes     342 comments"))
        post_layout.addWidget(QLabel("Emoji in retrieved comments: ❤️ 48   😍 31   👍 12"))
        layout.addWidget(post, 2)

        comments, comments_layout = self._panel("Comments & Replies", "Visible demo comment threads")
        for line in [
            "sarah_jones  Amazing! 😍  •  12 likes",
            "   Reply: Thank you! ❤️",
            "mike_smith  Beautiful view 👍  •  8 likes",
            "   Reply: Appreciate it!",
            "laura_brown  Love this place 🔥  •  5 likes",
        ]:
            comments_layout.addWidget(QLabel(line))
        comments_layout.addStretch()
        layout.addWidget(comments, 1)
        return page

    def _mentions_page(self) -> QWidget:
        """Create a mentions and tags timeline."""
        page = QWidget()
        layout = QVBoxLayout(page)
        panel, panel_layout = self._panel(
            "Mentions & Tags Center",
            "Only mentions and tags actually returned by an authorised provider are shown."
        )
        for entry in [
            "travel_diary mentioned your account in a post  •  Demo",
            "You were tagged in a photo  •  Demo",
            "foodie_life mentioned you in a story  •  Demo",
        ]:
            panel_layout.addWidget(QLabel("◉  " + entry))
        layout.addWidget(panel)
        return page

    def _stories_page(self) -> QWidget:
        """Create story and highlight collections in a familiar visual arrangement."""
        page = QWidget()
        layout = QVBoxLayout(page)
        panel, panel_layout = self._panel("Stories & Highlights", "Sample story circles and highlight collections.")
        row = QHBoxLayout()
        for label in ["Your Story", "Bali", "Japan", "Europe", "Food", "Nature"]:
            item = QLabel(f"◉\n{label}")
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setMinimumHeight(100)
            item.setStyleSheet("background:#202D49;border:2px solid #A855F7;border-radius:14px;padding:8px;")
            row.addWidget(item)
        panel_layout.addLayout(row)
        panel_layout.addWidget(QLabel("Select a collection in a live provider integration to open its media."))
        layout.addWidget(panel)
        return page

    def _insights_page(self) -> QWidget:
        """Show account type and visibility counts for loaded account records."""
        page = QWidget()
        layout = QVBoxLayout(page)
        panel, panel_layout = self._panel(
            "Account Classification & Insights",
            "This page does not infer gender from names or photos. Gender is unknown unless explicitly supplied as authorised aggregate data."
        )
        self.insights_label = QLabel("Load followers or following to calculate account category counts.")
        panel_layout.addWidget(self.insights_label)
        refresh = QPushButton("Refresh from current list")
        refresh.clicked.connect(self._refresh_insights)
        panel_layout.addWidget(refresh)
        layout.addWidget(panel)
        return page

    def _snapshots_page(self) -> QWidget:
        """Display locally saved snapshot metadata."""
        page = QWidget()
        layout = QVBoxLayout(page)
        panel, panel_layout = self._panel("Snapshots & History", "Snapshots are stored locally in SQLite.")
        refresh = QPushButton("Refresh Snapshot History")
        refresh.clicked.connect(self._refresh_snapshots)
        panel_layout.addWidget(refresh)
        self.snapshot_table = QTableWidget(0, 7)
        self.snapshot_table.setHorizontalHeaderLabels(
            ["ID", "Profile", "List", "Created", "Returned", "Expected", "Complete"]
        )
        self.snapshot_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        panel_layout.addWidget(self.snapshot_table)
        layout.addWidget(panel)
        return page

    def _compare_page(self) -> QWidget:
        """Provide snapshot comparison using the two most recent snapshots."""
        page = QWidget()
        layout = QVBoxLayout(page)
        panel, panel_layout = self._panel("Snapshot Comparison", "Compare the two latest snapshots of the same list.")
        compare = QPushButton("Compare Latest Snapshots")
        compare.setObjectName("PrimaryButton")
        compare.clicked.connect(self._compare_snapshots)
        panel_layout.addWidget(compare)
        self.compare_result = QLabel("No comparison run yet.")
        self.compare_result.setWordWrap(True)
        panel_layout.addWidget(self.compare_result)
        layout.addWidget(panel)
        return page

    def _export_page(self) -> QWidget:
        """Show export options and their availability."""
        page = QWidget()
        layout = QVBoxLayout(page)
        panel, panel_layout = self._panel("Export Center", "Export locally collected account-list data.")
        button = QPushButton("Export Current Account List as CSV")
        button.setObjectName("PrimaryButton")
        button.clicked.connect(self._export_accounts)
        panel_layout.addWidget(button)
        panel_layout.addWidget(QLabel("Supported in this starter release: CSV account-list export."))
        layout.addWidget(panel)
        return page

    def _settings_page(self) -> QWidget:
        """Show basic workspace and data-storage settings."""
        page = QWidget()
        layout = QVBoxLayout(page)
        panel, panel_layout = self._panel("Settings", "Local-first workspace settings.")
        panel_layout.addWidget(QLabel(f"Data directory: {self.data_dir}"))
        panel_layout.addWidget(QLabel("Theme: Premium Dark"))
        panel_layout.addWidget(QLabel("Provider: Local Demo Provider"))
        panel_layout.addWidget(QLabel("No Instagram password or session token is stored by this demo build."))
        layout.addWidget(panel)
        return page

    def _show_page(self, index: int) -> None:
        """Switch the visible page and update the selected navigation button."""
        self.pages.setCurrentIndex(index)
        for button_index, button in enumerate(self.nav_buttons):
            button.setChecked(button_index == index)
        if index == 8:
            self._refresh_snapshots()

    def _load_accounts(self, *_args) -> None:
        """Fetch a complete demo list and display truthful retrieval status."""
        self.current_list_type = self.list_selector.currentText()
        if self.current_list_type == "Followers":
            accounts, status = self.provider.get_followers(self.profile)
        else:
            accounts, status = self.provider.get_following(self.profile)

        self.current_accounts = accounts
        self.current_status = status
        self.completeness_label.setText(
            f"{status.returned_count} of {status.expected_count} loaded  •  "
            f"{'COMPLETE' if status.complete else 'PARTIAL'}  •  "
            f"{status.source}  •  {status.message}"
        )
        self._populate_account_table(accounts)
        logging.info("Loaded %s demo records for %s", len(accounts), self.current_list_type)

    def _populate_account_table(self, accounts: list[Account]) -> None:
        """Render account records into the explorer table."""
        self.account_table.setRowCount(len(accounts))
        for row_index, account in enumerate(accounts):
            values = [
                str(row_index + 1),
                account.display_name,
                account.username,
                account.account_type,
                account.visibility,
                "Yes" if account.verified else "No",
            ]
            for column, value in enumerate(values):
                self.account_table.setItem(row_index, column, QTableWidgetItem(value))

    def _filter_accounts(self, query: str) -> None:
        """Filter the currently loaded account records by name or username."""
        query = query.casefold().strip()
        filtered = [
            account
            for account in self.current_accounts
            if query in account.username.casefold()
            or query in account.display_name.casefold()
        ]
        self._populate_account_table(filtered)

    def _take_snapshot(self) -> None:
        """Save the currently loaded provider result as a local snapshot."""
        if not self.current_accounts or not self.current_status:
            QMessageBox.information(self, "No data loaded", "Load a follower/following list first.")
            return
        snapshot_id = self.database.save_snapshot(
            profile=self.profile,
            list_type=self.current_list_type,
            accounts=self.current_accounts,
            source=self.current_status.source,
            complete=self.current_status.complete,
            expected_count=self.current_status.expected_count,
        )
        QMessageBox.information(self, "Snapshot saved", f"Snapshot #{snapshot_id} saved locally.")
        self._refresh_snapshots()

    def _refresh_snapshots(self) -> None:
        """Reload snapshot metadata from SQLite."""
        if not hasattr(self, "snapshot_table"):
            return
        rows = self.database.list_snapshots()
        self.snapshot_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                str(row["id"]),
                row["profile"],
                row["list_type"],
                row["created_at"][:19].replace("T", " "),
                str(row["returned_count"]),
                str(row["expected_count"] if row["expected_count"] is not None else "Unknown"),
                "Yes" if row["complete"] else "No",
            ]
            for column, value in enumerate(values):
                self.snapshot_table.setItem(row_index, column, QTableWidgetItem(value))

    def _compare_snapshots(self) -> None:
        """Compare the latest two snapshots for the same profile and list type."""
        rows = self.database.list_snapshots()
        if len(rows) < 2:
            self.compare_result.setText("At least two snapshots are required.")
            return
        latest = rows[0]
        previous = next(
            (
                row for row in rows[1:]
                if row["profile"] == latest["profile"]
                and row["list_type"] == latest["list_type"]
            ),
            None,
        )
        if previous is None:
            self.compare_result.setText("No earlier snapshot exists for the same profile and list type.")
            return
        added, removed = compare_usernames(
            self.database.get_snapshot_usernames(previous["id"]),
            self.database.get_snapshot_usernames(latest["id"]),
        )
        self.compare_result.setText(
            f"Comparing snapshot #{previous['id']} with #{latest['id']}:\n"
            f"Newly observed: {len(added)}\nNo longer observed: {len(removed)}\n"
            f"New accounts: {', '.join(added[:20]) or 'None'}\n"
            f"Removed accounts: {', '.join(removed[:20]) or 'None'}"
        )

    def _refresh_insights(self) -> None:
        """Summarise only fields explicitly supplied by the current provider data."""
        if not self.current_accounts:
            self.insights_label.setText("Load a list in Followers & Following first.")
            return
        type_counts = classify_accounts(self.current_accounts)
        public_count = sum(item.visibility == "Public" for item in self.current_accounts)
        private_count = sum(item.visibility == "Private" for item in self.current_accounts)
        self.insights_label.setText(
            f"Accounts loaded: {len(self.current_accounts)}\n"
            f"Public: {public_count}  •  Private: {private_count}\n"
            f"Account categories: {type_counts}\n"
            "Gender breakdown: Not available from this demo provider; no gender is inferred."
        )

    def _export_accounts(self) -> None:
        """Export the current account list as a UTF-8 CSV file."""
        if not self.current_accounts:
            QMessageBox.information(self, "No data", "Load a list before exporting.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export account list", "accounts.csv", "CSV files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(["username", "display_name", "account_type", "visibility", "verified"])
            for account in self.current_accounts:
                writer.writerow([
                    account.username,
                    account.display_name,
                    account.account_type,
                    account.visibility,
                    account.verified,
                ])
        QMessageBox.information(self, "Export complete", f"Saved {len(self.current_accounts)} rows.")
