"""Instagram-style Home feed: stories tray, post cards, suggestions."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QScrollArea, QVBoxLayout, QWidget

from app.providers.base import Post, ProviderError
from app.ui.pages.base import Page
from app.ui.pages.common import avatar_pix, story_avatar
from app.ui.viewers import PostViewer, StoryViewer, media_pixmap, richtext
from app.ui.widgets import ClickLabel, Panel, label, scroll_wrap
from app.ui.workers import run_async
from app.utils import ago, fmt_count

CARD_W = 540


class PostCard(QFrame):
    def __init__(self, ctx, post: Post, posts: list[Post], idx: int, followers):
        super().__init__()
        self.setObjectName("PostCard")
        self.ctx, self.post, self.posts, self.idx, self.followers = ctx, post, posts, idx, followers
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 10)
        head = QHBoxLayout()
        head.setContentsMargins(12, 10, 12, 6)
        av = ClickLabel()
        av.setPixmap(avatar_pix(ctx, post.owner, "", 36))
        name = ClickLabel(post.owner)
        name.setStyleSheet("font-weight:700;")
        name.setCursor(Qt.CursorShape.PointingHandCursor)
        name.clicked.connect(lambda: ctx.open_profile.emit(post.owner))
        av.clicked.connect(lambda: ctx.open_profile.emit(post.owner))
        head.addWidget(av)
        v = QVBoxLayout()
        v.setSpacing(0)
        v.addWidget(name)
        v.addWidget(label(post.location, "Muted"))
        head.addLayout(v)
        head.addStretch()
        head.addWidget(label(ago(post.timestamp), "Muted"))
        lay.addLayout(head)
        self.img = ClickLabel()
        self.img.setCursor(Qt.CursorShape.PointingHandCursor)
        self.img.clicked.connect(self.open)
        self._set_image()
        lay.addWidget(self.img)
        row = QHBoxLayout()
        row.setContentsMargins(10, 4, 10, 0)
        favs = set(ctx.db.get_setting("favorites", []))
        self.heart = QPushButton("♥" if post.id in favs else "♡")
        self.heart.setObjectName("Flat")
        self.heart.setStyleSheet("font-size:17pt;")
        self.heart.setToolTip("Local favourite (does not like on Instagram)")
        self.heart.clicked.connect(self._fav)
        cm = QPushButton("💬")
        cm.setObjectName("Flat")
        cm.clicked.connect(self.open)
        row.addWidget(self.heart)
        row.addWidget(cm)
        row.addStretch()
        lay.addLayout(row)
        info = QVBoxLayout()
        info.setContentsMargins(14, 0, 14, 0)
        info.addWidget(label(f"{fmt_count(post.likes)} likes", "H2"))
        cap = label("", wrap=True)
        cap.setTextFormat(Qt.TextFormat.RichText)
        cap.setText(f"<b>{post.owner}</b> {richtext(post.caption, ctx.theme.accent_hex)}")
        info.addWidget(cap)
        more = ClickLabel(f"View all {fmt_count(post.comments_count)} comments")
        more.setObjectName("Muted")
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        more.clicked.connect(self.open)
        info.addWidget(more)
        lay.addLayout(info)

    def _set_image(self) -> None:
        m = self.post.media[0] if self.post.media else None
        if not m:
            return
        pm = media_pixmap(self.ctx, m, self.post.kind, on_ready=lambda _p: self._set_image())
        self.img.setPixmap(pm.scaled(CARD_W, CARD_W, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))
        self.img.setFixedHeight(min(CARD_W, self.img.pixmap().height()))

    def _fav(self) -> None:
        favs = list(self.ctx.db.get_setting("favorites", []))
        favs.remove(self.post.id) if self.post.id in favs else favs.append(self.post.id)
        self.ctx.db.save_setting("favorites", favs)
        self.heart.setText("♥" if self.post.id in favs else "♡")

    def open(self) -> None:
        PostViewer(self.ctx, self.posts, self.idx, self, self.followers).exec()


class FeedPage(Page):
    key = "feed"
    title = "Instagram view"
    subtitle = "Browse stories and posts the way you would in the app. Click anything to open it."

    def __init__(self, ctx):
        super().__init__(ctx)
        body = QHBoxLayout()
        center = QVBoxLayout()
        self.tray_scroll = QScrollArea()
        self.tray_scroll.setFixedHeight(112)
        self.tray_scroll.setWidgetResizable(True)
        self.tray_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.tray_scroll.viewport().setAutoFillBackground(False)
        self.tray = QWidget()
        self.tray.setObjectName("Transparent")
        self.tray_lay = QHBoxLayout(self.tray)
        self.tray_lay.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tray_scroll.setWidget(self.tray)
        center.addWidget(self.tray_scroll)
        self.feed = QWidget()
        self.feed_lay = QVBoxLayout(self.feed)
        self.feed_lay.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.feed_lay.setSpacing(14)
        center.addWidget(scroll_wrap(self.feed), 1)
        body.addLayout(center, 1)
        side = Panel("Suggested for you")
        side.setFixedWidth(290)
        self.side_lay = side.body
        body.addWidget(side, 0, Qt.AlignmentFlag.AlignTop)
        self.root.addLayout(body, 1)
        self.groups: list[tuple[str, list]] = []

    def _clear(self, lay) -> None:
        while lay.count():
            w = lay.takeAt(0).widget()
            if w:
                w.deleteLater()

    def on_show(self) -> None:
        super().on_show()
        prof = self.ctx.profile
        self._clear(self.feed_lay)
        self.feed_lay.addWidget(label("Loading…", "Muted"))

        def work():
            info = self.ctx.fetch("get_profile", prof)
            sugg = []
            try:
                sugg = self.ctx.registry.active.suggested_accounts()
            except ProviderError:
                pass
            saved = [r["username"] for r in self.ctx.db.list_profiles() if r["username"] != prof]
            users = [prof] + [s.username for s in sugg[:4]] + saved[:3]
            users = list(dict.fromkeys(users))
            posts, groups, errors = [], [], []
            for u in users:
                try:
                    posts += self.ctx.fetch("get_posts", u, 6)
                except ProviderError as e:
                    errors.append(str(e))
                try:
                    st = self.ctx.fetch("get_stories", u)
                    if st:
                        groups.append((u, st))
                except ProviderError:
                    pass
            posts.sort(key=lambda p: p.timestamp, reverse=True)
            return info, posts[:14], groups, sugg, errors

        run_async(work, self._loaded, lambda e: (self._clear(self.feed_lay),
                                                 self.feed_lay.addWidget(label(f"Could not load: {e}", wrap=True))))

    def _loaded(self, res) -> None:
        info, posts, self.groups, sugg, errors = res
        self._clear(self.tray_lay)
        seen = set(self.ctx.db.get_setting("seen_stories", []))
        for i, (user, stories) in enumerate(self.groups):
            col = QVBoxLayout()
            ring_lbl = ClickLabel()
            is_seen = all(s.id in seen for s in stories)
            ring_lbl.setPixmap(story_avatar(self.ctx, user, "", 64, is_seen))
            ring_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            ring_lbl.clicked.connect(lambda idx=i: self._open_stories(idx))
            col.addWidget(ring_lbl, 0, Qt.AlignmentFlag.AlignHCenter)
            name = label(user if len(user) <= 11 else user[:10] + "…", "Muted")
            name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            col.addWidget(name)
            w = QWidget()
            w.setObjectName("Transparent")
            w.setLayout(col)
            self.tray_lay.addWidget(w)
        if not self.groups:
            self.tray_lay.addWidget(label("No active stories available from this source "
                                          "(stories are available for your own account via the official API).",
                                          "Muted", wrap=True))
        self._clear(self.feed_lay)
        if not posts:
            self.feed_lay.addWidget(label(errors[0] if errors else "No posts available.", "Muted", wrap=True))
        for i, p in enumerate(posts):
            card = PostCard(self.ctx, p, posts, i, info.followers_count)
            card.setFixedWidth(CARD_W)
            self.feed_lay.addWidget(card)
        self._clear(self.side_lay)
        for s in sugg[:6] or []:
            row = QHBoxLayout()
            av = ClickLabel()
            av.setPixmap(avatar_pix(self.ctx, s.username, "", 36))
            av.clicked.connect(lambda u=s.username: self.ctx.open_profile.emit(u))
            row.addWidget(av)
            v = QVBoxLayout()
            v.setSpacing(0)
            v.addWidget(label(s.username))
            v.addWidget(label(f"{fmt_count(s.followers_count)} followers", "Muted"))
            row.addLayout(v, 1)
            b = QPushButton("View")
            b.clicked.connect(lambda _=False, u=s.username: self.ctx.open_profile.emit(u))
            row.addWidget(b)
            w = QWidget()
            w.setObjectName("Transparent")
            w.setLayout(row)
            self.side_lay.addWidget(w)
        if not sugg:
            self.side_lay.addWidget(label("Save profiles to see them here.", "Muted", wrap=True))

    def _open_stories(self, idx: int) -> None:
        StoryViewer(self.ctx, self.groups, idx, self).exec()
        self.on_show()
