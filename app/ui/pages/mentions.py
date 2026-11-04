"""Mentions & tags center."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLineEdit, QMenu, QPushButton

from app.providers.base import Mention, ProviderError
from app.services import analytics as an
from app.services import exporter as ex
from app.services.exporter import FORMATS
from app.ui.pages.base import Page
from app.ui.pdfout import save_pdf
from app.ui.widgets import fill_table, label, make_table
from app.ui.workers import run_async
from app.utils import fmt_dt

HEADERS = ["First detected", "Type", "By", "Mentioned", "Posted", "Preview"]


class MentionsPage(Page):
    key = "mentions"
    title = "Mentions & tags"
    subtitle = "@mentions in captions, comments, stories and tagged posts, with the time WE first detected each."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.rows: list = []
        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter by username or keyword…")
        self.search.textChanged.connect(self._filter)
        self.kind = QComboBox()
        self.kind.addItems(["All types", "caption", "comment", "story", "tag"])
        self.kind.currentTextChanged.connect(self._filter)
        scan = QPushButton("⟳ Scan now")
        scan.setObjectName("Primary")
        scan.clicked.connect(self._scan)
        exp = QPushButton("Export")
        menu = QMenu(self)
        for f in FORMATS:
            menu.addAction(f).triggered.connect(lambda _=False, fmt=f: self._export(fmt))
        exp.setMenu(menu)
        for w in (self.search, self.kind, scan, exp):
            bar.addWidget(w, 1 if w is self.search else 0)
        self.root.addLayout(bar)
        self.note = label("", "Muted", wrap=True)
        self.root.addWidget(self.note)
        self.table = make_table(HEADERS)
        self.table.doubleClicked.connect(lambda i: ctx.open_profile.emit(self.table.item(i.row(), 2).text()))
        self.root.addWidget(self.table, 1)
        self.chips = QHBoxLayout()
        self.root.addLayout(self.chips)

    def on_show(self) -> None:
        super().on_show()
        self.rows = self.ctx.db.list_mentions(self.ctx.profile)
        self._filter()

    def _filter(self) -> None:
        q, k = self.search.text().lower(), self.kind.currentText()
        out = [[fmt_dt(r["detected_at"]), r["source_type"], r["by_user"], r["mentioned_user"],
                fmt_dt(r["posted_at"] or ""), r["preview"]] for r in self.rows
               if (k == "All types" or r["source_type"] == k)
               and (not q or q in f"{r['by_user']} {r['mentioned_user']} {r['preview']}".lower())]
        fill_table(self.table, out)
        self.note.setText(f"{len(out)} mention(s). Story mentions and mentions in other people's comments are only "
                          "available where the source exposes them (the official API needs webhooks for stories). "
                          "Nothing is guessed.")

    def _scan(self) -> None:
        prof = self.ctx.profile

        def work():
            found, notes = 0, []
            for kind in ("get_mentions",):
                try:
                    for m in self.ctx.registry.call(kind, prof, fallback=False):
                        found += self.ctx.db.add_mention(prof, m)
                except ProviderError as exc:
                    notes.append((exc.status, str(exc)))
            try:
                for p in self.ctx.registry.call("get_posts", prof, 60):
                    for m in an.extract_mentions(p.caption):
                        found += self.ctx.db.add_mention(prof, Mention("caption", p.owner, m, p.id,
                                                                       p.caption[:140], p.timestamp))
            except ProviderError as exc:
                notes.append((exc.status, str(exc)))
            return found, notes

        def done(res):
            found, notes = res
            self.ctx.toast.emit("Mentions scan", f"{found} new mention(s) detected.")
            if notes:
                self.note.setText(" | ".join(f"{s}: {m}" for s, m in notes))
            self.rows = self.ctx.db.list_mentions(prof)
            self._filter()

        run_async(work, done, lambda e: self.note.setText(str(e)))

    def _export(self, fmt: str) -> None:
        data = [[self.table.item(r, c).text() for c in range(len(HEADERS))] for r in range(self.table.rowCount())]
        default = self.ctx.data_dir / "exports" / f"{self.ctx.profile}_mentions_{datetime.now():%Y%m%d}{FORMATS[fmt]}"
        path, _ = QFileDialog.getSaveFileName(self, "Export mentions", str(default), f"*{FORMATS[fmt]}")
        if not path:
            return
        p, title = Path(path), f"Mentions for @{self.ctx.profile}"
        {"CSV": lambda: ex.to_csv(p, HEADERS, data), "Excel": lambda: ex.to_xlsx(p, HEADERS, data, "Mentions"),
         "JSON": lambda: ex.to_json(p, HEADERS, data), "HTML": lambda: ex.to_html(p, HEADERS, data, title),
         "Markdown": lambda: ex.to_markdown(p, HEADERS, data, title),
         "PDF": lambda: save_pdf(p, HEADERS, data, title)}[fmt]()
        self.ctx.toast.emit("Exported", str(p))
