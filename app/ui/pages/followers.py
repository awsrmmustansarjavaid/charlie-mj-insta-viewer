"""Followers & Following explorer: complete lists, completeness, snapshots, export."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabBar,
    QTableView,
)

from app.providers import data_export
from app.providers.base import Account, ProviderError, RetrievalStatus
from app.services import analytics as an
from app.services.exporter import FORMATS
from app.ui.media import circle_crop, initials_avatar
from app.ui.pages.base import Page
from app.ui.pdfout import save_pdf
from app.ui.widgets import chip, label, status_chip
from app.ui.workers import run_async
from app.utils import fmt_dt

TABS = ["Followers", "Following", "Mutuals", "Not Following Back", "You Don't Follow Back"]
HEADERS = ["#", "Account", "Username", "Display name", "Type", "Visibility", "Verified", "Connected since"]


class AccountsModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.rows: list[Account] = []

    def set_rows(self, rows: list[Account]) -> None:
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):  # noqa: N802
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):  # noqa: N802
        return 0 if parent.isValid() else len(HEADERS)

    def headerData(self, s, o, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if o == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return HEADERS[s]

    def values(self, a: Account, row: int) -> list:
        v = "Unknown" if a.verified is None else ("Yes" if a.verified else "No")
        return [row + 1, "", a.username, a.display_name, a.account_type, a.visibility, v, fmt_dt(a.followed_at)[:10]]

    def data(self, idx, role=Qt.ItemDataRole.DisplayRole):
        if not idx.isValid():
            return None
        a, c = self.rows[idx.row()], idx.column()
        if role == Qt.ItemDataRole.DecorationRole and c == 1:
            return circle_crop(initials_avatar(a.username, 28), 28)
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.UserRole):
            val = self.values(a, idx.row())[c]
            if role == Qt.ItemDataRole.UserRole and c == 7:
                return a.followed_at
            return val if (role == Qt.ItemDataRole.UserRole or c != 1) else ""
        if role == Qt.ItemDataRole.ToolTipRole:
            return a.profile_url


class AccountsProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.text, self.kind, self.vis = "", "All types", "All visibility"
        self.setSortRole(Qt.ItemDataRole.UserRole)

    def set_filters(self, text: str, kind: str, vis: str) -> None:
        """Apply filters using the Qt >= 6.9 API when present (invalidateFilter is deprecated)."""
        begin = getattr(self, "beginFilterChange", None)
        if begin:
            begin()
        self.text, self.kind, self.vis = text, kind, vis
        if begin:
            self.endFilterChange()
        else:
            self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):  # noqa: N802
        a: Account = self.sourceModel().rows[row]
        if self.text and self.text not in f"{a.username} {a.display_name}".lower():
            return False
        if self.kind != "All types" and a.account_type != self.kind:
            return False
        return self.vis == "All visibility" or a.visibility == self.vis


class FollowersPage(Page):
    key = "followers"
    title = "Followers & Following"
    subtitle = "Every account in the list, with completeness shown honestly. Save snapshots to track change."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.followers: list[Account] = []
        self.following: list[Account] = []
        self.status: dict[str, RetrievalStatus | None] = {"followers": None, "following": None}
        self.snap_time: dict[str, str] = {}

        top = QHBoxLayout()
        self.tabbar = QTabBar()
        for t in TABS:
            self.tabbar.addTab(t)
        self.tabbar.currentChanged.connect(self._apply)
        top.addWidget(self.tabbar, 1)
        self.root.addLayout(top)

        comp = QHBoxLayout()
        self.loaded = label("", "H2")
        self.bar = QProgressBar()
        self.bar.setFixedWidth(220)
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.chip_box = QHBoxLayout()
        self.source = label("", "Muted")
        comp.addWidget(self.loaded)
        comp.addWidget(self.bar)
        comp.addLayout(self.chip_box)
        comp.addWidget(self.source, 1)
        self.root.addLayout(comp)

        tools = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search username or name…")
        self.search.textChanged.connect(self._filters)
        self.type_box = QComboBox()
        self.type_box.addItems(["All types", "Personal", "Business", "Creator", "Brand", "Media", "Unknown"])
        self.type_box.currentTextChanged.connect(self._filters)
        self.vis_box = QComboBox()
        self.vis_box.addItems(["All visibility", "Public", "Private", "Unknown"])
        self.vis_box.currentTextChanged.connect(self._filters)
        self.btn_refresh = QPushButton("⟳ Refresh && snapshot")
        self.btn_refresh.setObjectName("Primary")
        self.btn_refresh.clicked.connect(self._refresh)
        self.btn_import = QPushButton("📥 Import Instagram data export…")
        self.btn_import.clicked.connect(self._import)
        self.btn_export = QPushButton("Export")
        menu = QMenu(self)
        for f in FORMATS:
            menu.addAction(f).triggered.connect(lambda _=False, fmt=f: self._export(fmt))
        self.btn_export.setMenu(menu)
        for w in (self.search, self.type_box, self.vis_box):
            tools.addWidget(w, 1 if w is self.search else 0)
        for b in (self.btn_refresh, self.btn_import, self.btn_export):
            tools.addWidget(b)
        self.root.addLayout(tools)

        self.model = AccountsModel()
        self.proxy = AccountsProxy()
        self.proxy.setSourceModel(self.model)
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self._open)
        self.root.addWidget(self.table, 1)
        self.footer = label("", "Muted")
        self.root.addWidget(self.footer)
        ctx.profile_changed.connect(lambda _u: self.on_show())

    # data ---------------------------------------------------------------------
    def on_show(self) -> None:
        super().on_show()
        prof = self.ctx.profile
        self.followers, self.following = [], []
        for lt in ("followers", "following"):
            snap = self.ctx.db.latest_snapshot(prof, lt)
            if snap:
                setattr(self, lt, self.ctx.db.snapshot_accounts(snap["id"]))
                self.status[lt] = RetrievalStatus(snap["source"], snap["created_at"], snap["returned_count"],
                                                  snap["expected_count"], bool(snap["complete"]),
                                                  "Loaded from your latest saved snapshot.")
            else:
                self.status[lt] = None
        self._apply()

    def _current(self) -> tuple[list[Account], str]:
        i = self.tabbar.currentIndex()
        rel = an.relationships(self.followers, self.following)
        if i == 0:
            return self.followers, "followers"
        if i == 1:
            return self.following, "following"
        return rel[TABS[i]], "followers" if i == 4 else "following"

    def _apply(self) -> None:
        for i, t in enumerate(TABS):
            n = {0: len(self.followers), 1: len(self.following)}.get(i)
            if n is None:
                n = len(an.relationships(self.followers, self.following)[t])
            self.tabbar.setTabText(i, f"{t} ({n})")
        rows, base = self._current()
        self.model.set_rows(rows)
        self._filters()
        st = self.status.get(base)
        while self.chip_box.count():
            w = self.chip_box.takeAt(0).widget()
            if w:
                w.deleteLater()
        derived = self.tabbar.currentIndex() >= 2
        if st is None:
            self.loaded.setText("No data yet")
            self.bar.setValue(0)
            self.source.setText("Press 'Refresh && snapshot' or import your Instagram data export.")
            self.chip_box.addWidget(status_chip("HISTORICAL DATA REQUIRED"))
            return
        total = st.expected_count
        self.loaded.setText(f"{len(rows)} of {len(rows) if derived else (total if total is not None else '?')} loaded"
                            if not derived else f"{len(rows)} accounts (derived from both lists)")
        self.bar.setValue(100 if st.complete else (int(100 * st.returned_count / total) if total else 50))
        self.chip_box.addWidget(chip("Complete", "ChipOk") if st.complete else chip("Partial", "ChipWarn"))
        self.source.setText(f"{st.source} · {fmt_dt(st.retrieved_at)} · {st.message}")

    def _filters(self) -> None:
        self.proxy.set_filters(self.search.text().strip().lower(), self.type_box.currentText(),
                               self.vis_box.currentText())
        self.footer.setText(f"Showing {self.proxy.rowCount()} of {self.model.rowCount()} · double-click a row to open the profile")

    def _open(self, idx) -> None:
        u = self.proxy.data(self.proxy.index(idx.row(), 2))
        self.ctx.open_profile.emit(str(u))

    # actions ------------------------------------------------------------------------
    def _refresh(self) -> None:
        prof = self.ctx.profile
        self.btn_refresh.setEnabled(False)
        self.loaded.setText("Fetching…")
        self.bar.setRange(0, 0)

        def work(progress):
            out = {}
            for lt in ("followers", "following"):
                try:
                    out[lt] = self.ctx.snapshots.take(prof, lt, progress=progress)
                except ProviderError as exc:
                    out[lt] = exc
            return out

        def done(res):
            self.bar.setRange(0, 100)
            self.btn_refresh.setEnabled(True)
            errs = [f"{k}: {v}" for k, v in res.items() if isinstance(v, Exception)]
            if len(errs) == 2:
                QMessageBox.information(self, getattr(list(res.values())[0], "status", "Unavailable"),
                                        "\n\n".join(errs) + "\n\nTip: use 'Import Instagram data export…' for complete "
                                        "lists of your own account.")
            lines = [f"{k}: {len(v.accounts)} saved · +{len(v.added)} new · -{len(v.removed)} gone"
                     for k, v in res.items() if not isinstance(v, Exception) and v.had_previous]
            if lines:
                self.ctx.toast.emit("Snapshot saved", "\n".join(lines))
            self.ctx.data_changed.emit()
            self.on_show()

        run_async(work, done, lambda e: (self.btn_refresh.setEnabled(True), self.bar.setRange(0, 100),
                                         QMessageBox.warning(self, "Error", str(e))),
                  on_progress=lambda n, t: (self.bar.setRange(0, t or 0), self.bar.setValue(n),
                                            self.loaded.setText(f"Fetching… {n} of {t or '?'}")))

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import Instagram data export or list", "",
                                              "Instagram export / lists (*.zip *.json *.csv *.txt)")
        if not path:
            return
        prof, imported = self.ctx.profile, []
        types = ["followers", "following"] if path.lower().endswith(".zip") else \
            ["following" if self.tabbar.currentIndex() == 1 else "followers"]
        for lt in types:
            try:
                accounts, status = data_export.load_export(path, lt)
            except (ValueError, OSError, KeyError) as exc:
                if len(types) == 1:
                    QMessageBox.warning(self, "Import failed", str(exc))
                continue
            if accounts:
                res = self.ctx.snapshots.save(prof, lt, accounts, status, label="import")
                imported.append(f"{lt}: {len(accounts)} accounts ({len(res.added)} new, {len(res.removed)} gone)")
        if imported:
            QMessageBox.information(self, "Import complete", "\n".join(imported))
            self.ctx.data_changed.emit()
            self.on_show()
        elif len(types) == 2:
            QMessageBox.warning(self, "Nothing imported",
                                "No followers_*.json or following.json was found. In Instagram choose Accounts "
                                "Center → Your information and permissions → Download your information → "
                                "Followers and following, format JSON.")

    def _export(self, fmt: str) -> None:
        from app.services import exporter as ex

        rows, _ = self._current()
        shown = [self.proxy.mapToSource(self.proxy.index(r, 0)).row() for r in range(self.proxy.rowCount())]
        data = [[rows[i].username, rows[i].display_name, rows[i].account_type, rows[i].visibility,
                 "" if rows[i].verified is None else rows[i].verified, rows[i].followed_at[:10],
                 rows[i].profile_url] for i in shown]
        headers = ["username", "display_name", "type", "visibility", "verified", "connected_since", "profile_url"]
        name = TABS[self.tabbar.currentIndex()].lower().replace(" ", "_").replace("'", "")
        default = self.ctx.data_dir / "exports" / f"{self.ctx.profile}_{name}_{datetime.now():%Y%m%d}{FORMATS[fmt]}"
        path, _ = QFileDialog.getSaveFileName(self, f"Export {fmt}", str(default), f"*{FORMATS[fmt]}")
        if not path:
            return
        from pathlib import Path
        p = Path(path)
        title = f"@{self.ctx.profile} — {TABS[self.tabbar.currentIndex()]}"
        {"CSV": lambda: ex.to_csv(p, headers, data), "Excel": lambda: ex.to_xlsx(p, headers, data, name),
         "JSON": lambda: ex.to_json(p, headers, data), "HTML": lambda: ex.to_html(p, headers, data, title),
         "Markdown": lambda: ex.to_markdown(p, headers, data, title),
         "PDF": lambda: save_pdf(p, headers, data, title)}[fmt]()
        self.ctx.toast.emit("Exported", f"{len(data)} rows → {p}")
