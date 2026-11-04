"""Compare profiles, media library and the export / import / backup center."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app.providers.base import ProfileInfo, ProviderError
from app.services import analytics as an
from app.services import exporter as ex
from app.services.exporter import FORMATS
from app.ui.pages.base import Page
from app.ui.pdfout import save_pdf
from app.ui.widgets import Panel, fill_table, label, make_table, scroll_wrap
from app.ui.workers import run_async
from app.utils import fmt_count, fmt_dt, parse_username


def write_rows(fmt: str, path: Path, headers: list[str], rows: list[list], title: str) -> None:
    {"CSV": lambda: ex.to_csv(path, headers, rows), "Excel": lambda: ex.to_xlsx(path, headers, rows, title),
     "JSON": lambda: ex.to_json(path, headers, rows), "HTML": lambda: ex.to_html(path, headers, rows, title),
     "Markdown": lambda: ex.to_markdown(path, headers, rows, title),
     "PDF": lambda: save_pdf(path, headers, rows, title)}[fmt]()


def open_path(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])  # noqa: S603,S607
    else:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


class ComparePage(Page):
    key = "compare"
    title = "Compare profiles"
    subtitle = "Put two accounts side by side: audience, output, engagement and posting habits."

    def __init__(self, ctx):
        super().__init__(ctx)
        bar = QHBoxLayout()
        self.a, self.b = QLineEdit(), QLineEdit()
        self.a.setPlaceholderText("First username")
        self.b.setPlaceholderText("Second username")
        go = QPushButton("Compare")
        go.setObjectName("Primary")
        go.clicked.connect(self._go)
        for w in (self.a, self.b, go):
            bar.addWidget(w, 1 if w is not go else 0)
        self.root.addLayout(bar)
        self.table = make_table(["Metric", "—", "—"])
        self.root.addWidget(self.table, 1)
        self.note = label("", "Muted", wrap=True)
        self.root.addWidget(self.note)

    def on_show(self) -> None:
        super().on_show()
        if not self.a.text():
            self.a.setText(self.ctx.profile)
            self.b.setText("nature_lovers" if self.ctx.is_demo else "")

    def _stats(self, user: str):
        info: ProfileInfo = self.ctx.fetch("get_profile", user)
        try:
            posts = self.ctx.fetch("get_posts", user, 50)
        except ProviderError:
            posts = []
        likes = [p.likes for p in posts if p.likes is not None]
        cms = [p.comments_count for p in posts if p.comments_count is not None]
        rates = [r for p in posts if (r := an.engagement_rate(p, info.followers_count)) is not None]
        stamps = sorted(p.timestamp for p in posts if p.timestamp)
        per_week = "n/a"
        if len(stamps) > 1:
            span = (datetime.fromisoformat(stamps[-1]) - datetime.fromisoformat(stamps[0])).days or 1
            per_week = f"{len(stamps) / span * 7:.1f}"
        return [fmt_count(info.followers_count), fmt_count(info.following_count), fmt_count(info.posts_count),
                info.account_type, fmt_count(int(sum(likes) / len(likes))) if likes else "n/a",
                fmt_count(int(sum(cms) / len(cms))) if cms else "n/a",
                f"{sum(rates) / len(rates):.2f}%" if rates else "n/a", per_week,
                ", ".join("#" + t for t, _ in an.hashtag_frequency(posts, 4)) or "–"]

    def _go(self) -> None:
        ua, ub = parse_username(self.a.text()), parse_username(self.b.text())
        if not ua or not ub:
            return

        def work():
            return self._stats(ua), self._stats(ub)

        def done(res):
            self.table.setHorizontalHeaderLabels(["Metric", f"@{ua}", f"@{ub}"])
            labels = ["Followers", "Following", "Posts", "Account type", "Avg. likes", "Avg. comments",
                      "Avg. engagement rate", "Posts per week", "Top hashtags"]
            fill_table(self.table, [[l, x, y] for l, x, y in zip(labels, *res, strict=False)])
            self.note.setText(f"Source: {self.ctx.provider_label}. Metrics use the most recent posts the source returned.")

        run_async(work, done, lambda e: self.note.setText(f"{getattr(e, 'status', '')}: {e}"))


class LibraryPage(Page):
    key = "library"
    title = "Library & downloads"
    subtitle = "Everything you have saved from stories, highlights, posts and reels, with duplicate detection."

    def __init__(self, ctx):
        super().__init__(ctx)
        bar = QHBoxLayout()
        for text, fn in (("Open downloads folder", lambda: open_path(ctx.data_dir / "downloads")),
                         ("Open selected file", self._open_file), ("Remove record", self._remove)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            bar.addWidget(b)
        bar.addStretch()
        self.count = label("", "Muted")
        bar.addWidget(self.count)
        self.root.addLayout(bar)
        self.table = make_table(["When", "Profile", "Kind", "Status", "File"])
        self.table.doubleClicked.connect(lambda _i: self._open_file())
        self.root.addWidget(self.table, 1)
        ctx.data_changed.connect(self._fill)

    def on_show(self) -> None:
        super().on_show()
        self._fill()

    def _fill(self) -> None:
        rows = self.ctx.db.list_downloads()
        fill_table(self.table, [[fmt_dt(r["created_at"]), r["profile"], r["kind"], r["status"], r["path"]] for r in rows])
        favs = len(self.ctx.db.get_setting("favorites", []))
        self.count.setText(f"{len(rows)} records · {favs} local favourites")

    def _open_file(self) -> None:
        r = self.table.selectionModel().selectedRows()
        if r:
            p = Path(self.table.item(r[0].row(), 4).text())
            if p.exists():
                open_path(p)

    def _remove(self) -> None:
        QMessageBox.information(self, "Records", "Download records are kept as an audit trail. Delete the file "
                                "itself from the downloads folder to free space.")


class ExportPage(Page):
    key = "export"
    title = "Export, import & backup"
    subtitle = "Reports in CSV, Excel, PDF, HTML, JSON or Markdown · username lists · full database backup."

    DATASETS = ["Followers (latest snapshot)", "Following (latest snapshot)", "Saved profiles", "Activity timeline",
                "Mentions", "Download history", "Snapshot list"]

    def __init__(self, ctx):
        super().__init__(ctx)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        p1 = Panel("Export a report")
        row = QHBoxLayout()
        self.dataset = QComboBox()
        self.dataset.addItems(self.DATASETS)
        self.fmt = QComboBox()
        self.fmt.addItems(list(FORMATS))
        go = QPushButton("Export…")
        go.setObjectName("Primary")
        go.clicked.connect(self._export)
        for w in (self.dataset, self.fmt, go):
            row.addWidget(w)
        row.addStretch()
        p1.body.addLayout(row)
        lay.addWidget(p1)

        p2 = Panel("Saved usernames", "Move your list of tracked usernames between computers (JSON or CSV).")
        r2 = QHBoxLayout()
        for text, fn in (("Export usernames (JSON)", self._export_names), ("Import usernames (JSON/CSV/TXT)", self._import_names)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            r2.addWidget(b)
        r2.addStretch()
        p2.body.addLayout(r2)
        lay.addWidget(p2)

        p3 = Panel("Database backup & restore", "Backups are complete copies of your local database (snapshots, events, "
                   "mentions, monitors, settings). Credentials are never stored in the database.")
        r3 = QHBoxLayout()
        for text, fn in (("Backup now", self._backup), ("Restore from backup…", self._restore)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            r3.addWidget(b)
        r3.addStretch()
        p3.body.addLayout(r3)
        lay.addWidget(p3)
        lay.addStretch()
        self.root.addWidget(scroll_wrap(inner), 1)

    def _dataset(self) -> tuple[list[str], list[list], str]:
        d, prof = self.dataset.currentText(), self.ctx.profile
        db = self.ctx.db
        if d.startswith(("Followers", "Following")):
            lt = "followers" if d.startswith("Followers") else "following"
            snap = db.latest_snapshot(prof, lt)
            accs = db.snapshot_accounts(snap["id"]) if snap else []
            return (["username", "display_name", "type", "visibility", "verified", "connected_since"],
                    [[a.username, a.display_name, a.account_type, a.visibility, "" if a.verified is None else a.verified,
                      a.followed_at[:10]] for a in accs], f"@{prof} {lt}")
        if d == "Saved profiles":
            return (["username", "display_name", "followers", "following", "posts", "type", "notes", "collection", "tags"],
                    [[r["username"], r["display_name"], r["followers_count"], r["following_count"], r["posts_count"],
                      r["account_type"], r["notes"], r["collection"], r["tags"]] for r in db.list_profiles()], "Saved profiles")
        if d == "Activity timeline":
            return (["detected_at", "profile", "kind", "detail"],
                    [[e["detected_at"], e["profile"], e["kind"], e["detail"]] for e in db.list_events(limit=100000)], "Activity")
        if d == "Mentions":
            return (["first_detected", "type", "by", "mentioned", "posted_at", "preview"],
                    [[m["detected_at"], m["source_type"], m["by_user"], m["mentioned_user"], m["posted_at"], m["preview"]]
                     for m in db.list_mentions()], "Mentions")
        if d == "Download history":
            return (["when", "profile", "kind", "status", "path"],
                    [[r["created_at"], r["profile"], r["kind"], r["status"], r["path"]] for r in db.list_downloads()], "Downloads")
        return (["id", "profile", "list", "taken", "source", "returned", "expected", "complete"],
                [[s["id"], s["profile"], s["list_type"], s["created_at"], s["source"], s["returned_count"],
                  s["expected_count"], bool(s["complete"])] for s in db.list_snapshots()], "Snapshots")

    def _export(self) -> None:
        headers, rows, title = self._dataset()
        fmt = self.fmt.currentText()
        default = self.ctx.data_dir / "exports" / f"{title.replace(' ', '_').replace('@', '')}_{datetime.now():%Y%m%d}{FORMATS[fmt]}"
        path, _ = QFileDialog.getSaveFileName(self, "Export", str(default), f"*{FORMATS[fmt]}")
        if path:
            write_rows(fmt, Path(path), headers, rows, title)
            self.ctx.toast.emit("Exported", f"{len(rows)} rows → {path}")

    def _export_names(self) -> None:
        names = sorted({r["username"] for r in self.ctx.db.list_profiles()} | {m["profile"] for m in self.ctx.db.list_monitors()})
        path, _ = QFileDialog.getSaveFileName(self, "Export usernames", str(self.ctx.data_dir / "exports" / "usernames.json"), "*.json")
        if path:
            Path(path).write_text(json.dumps({"usernames": names}, indent=2), encoding="utf-8")
            self.ctx.toast.emit("Exported", f"{len(names)} usernames")

    def _import_names(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import usernames", "", "Lists (*.json *.csv *.txt)")
        if not path:
            return
        text = Path(path).read_text(encoding="utf-8-sig")
        try:
            if text.lstrip().startswith(("{", "[")):
                data = json.loads(text)
                names = data.get("usernames", []) if isinstance(data, dict) else data
            else:
                names = [r[0] for r in csv.reader(text.splitlines()) if r and r[0].lower() != "username"]
        except (ValueError, KeyError) as exc:
            QMessageBox.warning(self, "Import failed", str(exc))
            return
        added = 0
        for n in names:
            u = parse_username(str(n))
            if u:
                self.ctx.db.upsert_profile(ProfileInfo(username=u), "import")
                added += 1
        self.ctx.data_changed.emit()
        QMessageBox.information(self, "Imported", f"{added} usernames added to Saved profiles.")

    def _backup(self) -> None:
        p = self.ctx.db.backup_to(self.ctx.data_dir / "backups" / f"backup_{datetime.now():%Y%m%d_%H%M%S}.sqlite3")
        self.ctx.toast.emit("Backup created", str(p))

    def _restore(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Restore backup", str(self.ctx.data_dir / "backups"), "*.sqlite3")
        if not path:
            return
        if QMessageBox.question(self, "Restore", "Replace the current database with this backup? A safety copy of "
                                "the current one is kept next to it.") != QMessageBox.StandardButton.Yes:
            return
        try:
            self.ctx.db.restore_from(Path(path))
        except ValueError as exc:
            QMessageBox.warning(self, "Restore failed", str(exc))
            return
        self.ctx.invalidate()
        QMessageBox.information(self, "Restored", "Backup restored.")
