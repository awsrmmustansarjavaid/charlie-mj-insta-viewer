"""Profile explorer with highlights and a tabbed post grid."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.providers.base import Highlight, Post, ProfileInfo
from app.ui.pages.base import Page
from app.ui.pages.common import avatar_pix, story_avatar, tile_pix
from app.ui.viewers import PostViewer, StoryViewer, download_media
from app.ui.widgets import ClickLabel, chip, label, scroll_wrap, status_chip
from app.ui.workers import run_async
from app.utils import fmt_count, parse_username

TILE = 200


class ProfilePage(Page):
    key = "profile"
    title = "Profile explorer"
    subtitle = "Look up any username your active source can provide: profile, highlights, posts and reels."

    def __init__(self, ctx):
        super().__init__(ctx)
        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Username or instagram.com/… link, then press Enter")
        self.search.returnPressed.connect(self._go)
        self.recent = QComboBox()
        self.recent.setMinimumWidth(170)
        self.recent.activated.connect(lambda: self._open_user(self.recent.currentText()))
        go = QPushButton("Open")
        go.setObjectName("Primary")
        go.clicked.connect(self._go)
        bar.addWidget(self.search, 1)
        bar.addWidget(go)
        bar.addWidget(self.recent)
        self.root.addLayout(bar)

        self.body_widget = QWidget()
        self.body = QVBoxLayout(self.body_widget)
        self.body.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.header = QHBoxLayout()
        self.avatar = ClickLabel()
        self.header.addWidget(self.avatar)
        info = QVBoxLayout()
        self.name = label("", "PageTitle")
        self.counts = label("")
        self.bio = label("", wrap=True)
        self.tags = QHBoxLayout()
        info.addWidget(self.name)
        info.addLayout(self.tags)
        info.addWidget(self.counts)
        info.addWidget(self.bio)
        actions = QHBoxLayout()
        for text, fn, primary in (("📸 Snapshot lists", self._snapshot, True), ("👁 Monitor", self._monitor, False),
                                  ("💾 Save profile", self._save, False), ("⬇ Download all posts", self._dl_all, False),
                                  ("↗ Followers && following", lambda: self.ctx.navigate.emit("followers"), False)):
            b = QPushButton(text)
            if primary:
                b.setObjectName("Primary")
            b.clicked.connect(fn)
            actions.addWidget(b)
        actions.addStretch()
        info.addLayout(actions)
        self.header.addLayout(info, 1)
        self.body.addLayout(self.header)
        self.hl_box = QHBoxLayout()
        self.hl_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.body.addLayout(self.hl_box)
        self.tabs = QTabWidget()
        self.grid_widget, self.grid = self._grid()
        self.reels_widget, self.reels_grid = self._grid()
        self.tagged = QListWidget()
        self.tabs.addTab(self.grid_widget, "▦ Posts")
        self.tabs.addTab(self.reels_widget, "🎬 Reels")
        self.tabs.addTab(self.tagged, "🏷 Tagged / mentions")
        self.body.addWidget(self.tabs)
        self.root.addWidget(scroll_wrap(self.body_widget), 1)
        self.info: ProfileInfo | None = None
        self.posts: list[Post] = []
        self.highlights: list[Highlight] = []
        ctx.open_profile.connect(self._open_user)

    @staticmethod
    def _grid():
        w = QWidget()
        w.setObjectName("Transparent")
        g = QGridLayout(w)
        g.setSpacing(4)
        g.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        return w, g

    # ---------------------------------------------------------------------------
    def _go(self) -> None:
        self._open_user(parse_username(self.search.text()))

    def _open_user(self, username: str) -> None:
        if username:
            self.ctx.set_profile(username)
            self.ctx.navigate.emit("profile")

    def on_show(self) -> None:
        super().on_show()
        prof = self.ctx.profile
        self.search.setText(prof)
        self.recent.clear()
        self.recent.addItems(["Recent searches…"] + self.ctx.db.list_searches())
        self.name.setText(f"@{prof}")
        self.counts.setText("Loading…")

        def work():
            info = self.ctx.fetch("get_profile", prof)
            posts = self.ctx.fetch("get_posts", prof, 60)
            return info, posts

        run_async(work, self._loaded, self._failed)

        def hl():
            return self.ctx.fetch("get_highlights", prof)

        run_async(hl, self._hl_loaded, lambda e: self._hl_loaded(e))

        def tg():
            return self.ctx.fetch("get_mentions", prof)

        run_async(tg, self._tags_loaded, lambda e: self._tags_loaded(e))

    def _failed(self, exc) -> None:
        status = getattr(exc, "status", "PROVIDER UNAVAILABLE")
        self.counts.setText(f"{status}: {exc}")
        self.bio.setText("")

    def _clear(self, lay) -> None:
        while lay.count():
            w = lay.takeAt(0).widget()
            if w:
                w.deleteLater()

    def _loaded(self, res) -> None:
        self.info, self.posts = res
        i = self.info
        self.avatar.setPixmap(avatar_pix(self.ctx, i.username, i.avatar, 120,
                                         lambda pm: self.avatar.setPixmap(pm)))
        self.name.setText(("✔ " if i.verified else "") + f"@{i.username}")
        self.counts.setText(f"<b>{fmt_count(i.posts_count)}</b> posts   <b>{fmt_count(i.followers_count)}</b> "
                            f"followers   <b>{fmt_count(i.following_count)}</b> following")
        self.bio.setText(f"<b>{i.display_name}</b><br>{i.bio.replace(chr(10), '<br>')}"
                         + (f"<br><a href='https://{i.external_url}'>{i.external_url}</a>" if i.external_url else ""))
        self.bio.setTextFormat(Qt.TextFormat.RichText)
        self._clear(self.tags)
        for t in (i.account_type, i.visibility, i.category):
            if t and t != "Unknown":
                self.tags.addWidget(chip(t))
        self.tags.addStretch()
        self._fill_grid(self.grid, self.posts)
        self._fill_grid(self.reels_grid, [p for p in self.posts if p.kind in ("REEL", "VIDEO")])

    def _fill_grid(self, grid: QGridLayout, posts: list[Post]) -> None:
        while grid.count():
            w = grid.takeAt(0).widget()
            if w:
                w.deleteLater()
        if not posts:
            grid.addWidget(label("Nothing to show from this source.", "Muted"), 0, 0)
        for n, p in enumerate(posts):
            tile = ClickLabel()
            tile.setFixedSize(TILE, TILE)
            tile.setPixmap(tile_pix(self.ctx, p, TILE, on_ready=lambda t=tile, pp=p: t.setPixmap(tile_pix(self.ctx, pp, TILE))))
            tile.setCursor(Qt.CursorShape.PointingHandCursor)
            tile.setToolTip(f"♥ {fmt_count(p.likes)}   💬 {fmt_count(p.comments_count)}")
            tile.clicked.connect(lambda pp=p, lst=posts: self._open_post(lst, lst.index(pp)))
            grid.addWidget(tile, n // 3, n % 3)

    def _open_post(self, lst: list[Post], idx: int) -> None:
        PostViewer(self.ctx, lst, idx, self, self.info.followers_count if self.info else None).exec()

    def _hl_loaded(self, res) -> None:
        self._clear(self.hl_box)
        if isinstance(res, Exception):
            status = getattr(res, "status", "")
            self.hl_box.addWidget(status_chip(status) if status else label(str(res)))
            self.hl_box.addWidget(label("Highlights are not provided by this source.", "Muted"))
            return
        self.highlights = res
        seen = set(self.ctx.db.get_setting("seen_stories", []))
        for i, h in enumerate(res):
            col = QVBoxLayout()
            lb = ClickLabel()
            lb.setPixmap(story_avatar(self.ctx, h.title, h.cover, 64, all(s.id in seen for s in h.stories)))
            lb.setCursor(Qt.CursorShape.PointingHandCursor)
            lb.clicked.connect(lambda idx=i: self._open_highlight(idx))
            col.addWidget(lb, 0, Qt.AlignmentFlag.AlignHCenter)
            t = label(h.title, "Muted")
            t.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            col.addWidget(t)
            w = QWidget()
            w.setObjectName("Transparent")
            w.setLayout(col)
            self.hl_box.addWidget(w)

    def _open_highlight(self, idx: int) -> None:
        h = self.highlights[idx]
        StoryViewer(self.ctx, [(f"{h.owner} · {h.title}", h.stories)], 0, self).exec()

    def _tags_loaded(self, res) -> None:
        self.tagged.clear()
        if isinstance(res, Exception):
            self.tagged.addItem(f"{getattr(res, 'status', 'UNAVAILABLE')}: {res}")
            return
        for m in res:
            self.tagged.addItem(f"[{m.source_type}] @{m.by_user} → @{m.mentioned_user} — {m.preview}")

    # actions -----------------------------------------------------------------------
    def _snapshot(self) -> None:
        self.ctx.navigate.emit("followers")
        self.ctx.toast.emit("Tip", "Use 'Refresh & snapshot' on the Followers page.")

    def _monitor(self) -> None:
        self.ctx.db.upsert_monitor(self.ctx.profile, 60)
        self.ctx.data_changed.emit()
        self.ctx.toast.emit("Monitoring", f"@{self.ctx.profile} is now monitored every 60 minutes.")

    def _save(self) -> None:
        if self.info:
            self.ctx.db.upsert_profile(self.info, self.ctx.registry.active_name)
            self.ctx.toast.emit("Saved", f"@{self.info.username} saved to your profiles.")

    def _dl_all(self) -> None:
        n = 0
        for p in self.posts:
            for k, m in enumerate(p.media):
                download_media(self.ctx, p.owner, f"{p.id}_{k}", m, p.kind, self)
                n += 1
        QMessageBox.information(self, "Downloads", f"Saved up to {n} files to the downloads folder.")
