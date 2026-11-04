"""Snapshot history, snapshot comparison and the activity timeline."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QSplitter, QTabWidget, QVBoxLayout, QWidget

from app.services import exporter as ex
from app.ui.pages.base import Page
from app.ui.widgets import MetricCard, Panel, fill_table, label, make_table
from app.utils import fmt_dt


class SnapshotsPage(Page):
    key = "snapshots"
    title = "Snapshots & compare"
    subtitle = "Pick any two snapshots to see exactly who was added or removed between them."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.rows: list = []
        tabs = QTabWidget()
        # history tab
        hist = QWidget()
        hl = QVBoxLayout(hist)
        bar = QHBoxLayout()
        self.kind = QComboBox()
        self.kind.addItems(["followers", "following"])
        self.kind.currentTextChanged.connect(self.on_show)
        view = QPushButton("View accounts")
        view.clicked.connect(self._view)
        delete = QPushButton("Delete snapshot")
        delete.clicked.connect(self._delete)
        bar.addWidget(self.kind)
        bar.addStretch()
        bar.addWidget(view)
        bar.addWidget(delete)
        hl.addLayout(bar)
        self.table = make_table(["ID", "Taken", "Source", "Accounts", "Expected", "Complete", "Label"])
        hl.addWidget(self.table)
        tabs.addTab(hist, "History")
        # compare tab
        cmp_ = QWidget()
        cl = QVBoxLayout(cmp_)
        sel = QHBoxLayout()
        self.a = QComboBox()
        self.b = QComboBox()
        for w in (self.a, self.b):
            w.setMinimumWidth(300)
        go = QPushButton("Compare")
        go.setObjectName("Primary")
        go.clicked.connect(self._compare)
        exp = QPushButton("Export diff (CSV)")
        exp.clicked.connect(self._export)
        sel.addWidget(label("Older:"))
        sel.addWidget(self.a)
        sel.addWidget(label("Newer:"))
        sel.addWidget(self.b)
        sel.addWidget(go)
        sel.addWidget(exp)
        sel.addStretch()
        cl.addLayout(sel)
        cards = QHBoxLayout()
        self.m_add, self.m_rem, self.m_net = MetricCard("Added"), MetricCard("Removed"), MetricCard("Net change")
        for m in (self.m_add, self.m_rem, self.m_net):
            cards.addWidget(m)
        cl.addLayout(cards)
        split = QSplitter()
        pa, pr = Panel("Added (in newer, not in older)"), Panel("Removed (in older, not in newer)")
        self.t_add, self.t_rem = make_table(["Username"]), make_table(["Username"])
        pa.body.addWidget(self.t_add)
        pr.body.addWidget(self.t_rem)
        split.addWidget(pa)
        split.addWidget(pr)
        cl.addWidget(split, 1)
        self.note = label("'Removed' means no longer present in the later snapshot; it does not say when the person "
                          "unfollowed, only when we first noticed.", "Muted", wrap=True)
        cl.addWidget(self.note)
        tabs.addTab(cmp_, "Compare two snapshots")
        self.root.addWidget(tabs, 1)
        self.added: list[str] = []
        self.removed: list[str] = []

    def on_show(self) -> None:
        super().on_show()
        self.rows = self.ctx.db.list_snapshots(self.ctx.profile, self.kind.currentText())
        fill_table(self.table, [[r["id"], fmt_dt(r["created_at"]), r["source"], r["returned_count"],
                                 r["expected_count"] if r["expected_count"] is not None else "?",
                                 "yes" if r["complete"] else "partial", r["label"]] for r in self.rows])
        for box in (self.a, self.b):
            box.clear()
            for r in self.rows:
                box.addItem(f"#{r['id']} · {fmt_dt(r['created_at'])} · {r['returned_count']} accounts", r["id"])
        if len(self.rows) >= 2:
            self.a.setCurrentIndex(1)
            self.b.setCurrentIndex(0)

    def _selected(self) -> int | None:
        r = self.table.selectionModel().selectedRows()
        return int(self.table.item(r[0].row(), 0).text()) if r else None

    def _view(self) -> None:
        sid = self._selected()
        if sid:
            accs = self.ctx.db.snapshot_accounts(sid)
            QMessageBox.information(self, f"Snapshot #{sid}", f"{len(accs)} accounts.\nFirst 30:\n" +
                                    "\n".join("@" + a.username for a in accs[:30]))

    def _delete(self) -> None:
        sid = self._selected()
        if sid and QMessageBox.question(self, "Delete", f"Delete snapshot #{sid}?") == QMessageBox.StandardButton.Yes:
            self.ctx.db.delete_snapshot(sid)
            self.on_show()

    def _compare(self) -> None:
        ida, idb = self.a.currentData(), self.b.currentData()
        if ida is None or idb is None:
            QMessageBox.information(self, "Need two snapshots", "Take at least two snapshots first.")
            return
        self.added, self.removed = self.ctx.snapshots.diff(ida, idb)
        fill_table(self.t_add, [[u] for u in self.added])
        fill_table(self.t_rem, [[u] for u in self.removed])
        self.m_add.set(str(len(self.added)))
        self.m_rem.set(str(len(self.removed)))
        self.m_net.set(f"{len(self.added) - len(self.removed):+d}")

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export diff", str(self.ctx.data_dir / "exports" /
                                              f"diff_{datetime.now():%Y%m%d_%H%M}.csv"), "*.csv")
        if path:
            ex.to_csv(Path(path), ["change", "username"],
                      [["added", u] for u in self.added] + [["removed", u] for u in self.removed])
            self.ctx.toast.emit("Exported", path)


class TimelinePage(Page):
    key = "timeline"
    title = "Activity timeline"
    subtitle = "Every change the app has detected, newest first. Times mean 'first detected by this app'."

    ICONS = {"baseline": "📌", "new_follower": "➕", "lost_follower": "➖", "new_following": "👤", "lost_following": "🚫",
             "new_post": "🖼", "new_reel": "🎬", "new_story": "⭕", "mention": "@", "count_change": "🔢"}

    def __init__(self, ctx):
        super().__init__(ctx)
        bar = QHBoxLayout()
        self.kind = QComboBox()
        self.kind.currentTextChanged.connect(self._fill)
        self.scope = QComboBox()
        self.scope.addItems(["Active profile", "All profiles"])
        self.scope.currentTextChanged.connect(self._fill)
        bar.addWidget(self.kind)
        bar.addWidget(self.scope)
        bar.addStretch()
        self.root.addLayout(bar)
        self.table = make_table(["Detected", "Profile", "Event", "Details"])
        self.root.addWidget(self.table, 1)

    def on_show(self) -> None:
        super().on_show()
        self.kind.blockSignals(True)
        cur = self.kind.currentText()
        kinds = sorted({e["kind"] for e in self.ctx.db.list_events(limit=2000)})
        self.kind.clear()
        self.kind.addItems(["All events"] + kinds)
        if cur in kinds:
            self.kind.setCurrentText(cur)
        self.kind.blockSignals(False)
        self._fill()

    def _fill(self) -> None:
        prof = self.ctx.profile if self.scope.currentText() == "Active profile" else None
        k = self.kind.currentText()
        rows = self.ctx.db.list_events(prof, None if k in ("All events", "") else k)
        fill_table(self.table, [[fmt_dt(e["detected_at"]), e["profile"],
                                 f"{self.ICONS.get(e['kind'], '•')} {e['kind']}", e["detail"]] for e in rows])
