"""Instagram-style full-screen viewers: PostViewer and StoryViewer."""

from __future__ import annotations

import html
import logging
import re

from PySide6.QtCore import QEvent, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from app.providers.base import MediaItem, Post, Story
from app.services import analytics as an
from app.services.downloader import fetch_url, is_duplicate, target_path
from app.ui.context import AppContext
from app.ui.media import circle_crop, initials_avatar
from app.ui.widgets import BarChart, ClickLabel, chip, label, scroll_wrap
from app.ui.workers import run_async
from app.utils import ago, ago_long, fmt_count, fmt_dt

log = logging.getLogger(__name__)

try:  # optional: real video playback
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
    from PySide6.QtMultimediaWidgets import QVideoWidget
    HAVE_VIDEO = True
except Exception:  # noqa: BLE001
    HAVE_VIDEO = False


# ---------------------------------------------------------------------------
def media_pixmap(ctx: AppContext, m: MediaItem, kind: str, on_ready=None) -> QPixmap:
    """Pixmap for a media item (portrait for reels, square otherwise)."""
    portrait = kind in ("REEL", "STORY")
    w, h = (720, 1280) if portrait else (1080, 1080)
    src = m.url if m.url else (f"seed:{m.seed}" if m.seed and not m.seed.startswith("http") else "")
    return ctx.pix(src, w, h, on_ready)


def download_media(ctx: AppContext, owner: str, item_id: str, m: MediaItem, kind: str, parent: QWidget) -> None:
    """Save the media file to the downloads folder (de-duplicated, recorded)."""
    folder = ctx.data_dir / "downloads"
    remote = m.seed if (m.is_video and m.seed.startswith("https://")) else (m.url if m.url.startswith("https://") else "")
    if remote:
        ext = ".mp4" if m.is_video else ".jpg"
        dest = target_path(folder, owner, item_id, ext)

        def work():
            fetch_url(remote, dest)
            return dest

        def done(path):
            _finish(ctx, owner, item_id, kind, path, parent)

        run_async(work, done, lambda e: QMessageBox.warning(parent, "Download failed", str(e)))
        return
    dest = target_path(folder, owner, item_id, ".png")
    media_pixmap(ctx, m, kind).save(str(dest), "PNG")
    _finish(ctx, owner, item_id, kind, dest, parent)


def _finish(ctx: AppContext, owner, item_id, kind, path, parent) -> None:
    dup = is_duplicate(path)
    if dup:
        path.unlink(missing_ok=True)
        ctx.db.add_download(owner, item_id, kind, str(dup), "duplicate")
        ctx.toast.emit("Already downloaded", dup.name)
        return
    ctx.db.add_download(owner, item_id, kind, str(path), "ok")
    ctx.data_changed.emit()
    ctx.toast.emit("Downloaded", str(path))


def richtext(text: str, accent: str) -> str:
    """Escape text and colourise #hashtags / @mentions in a single pass
    (so inserted markup can never be re-matched)."""
    t = html.escape(text, quote=False).replace("\n", "<br>")

    def repl(m: re.Match) -> str:
        if m.group(1):
            return f'<a style="color:{accent};text-decoration:none" href="user:{m.group(1)}">@{m.group(1)}</a>'
        return f'<span style="color:{accent}">#{m.group(2)}</span>'

    return re.sub(r"@([A-Za-z0-9._]+)|#(\w+)", repl, t)


# ---------------------------------------------------------------------------
class PostViewer(QDialog):
    """Large media on the left; caption, comments, replies and analysis on the right."""

    def __init__(self, ctx: AppContext, posts: list[Post], index: int, parent=None, followers: int | None = None):
        super().__init__(parent)
        self.ctx, self.posts, self.i, self.m = ctx, posts, index, 0
        self.followers = followers
        self.comments: list = []
        self.reply_to: tuple[str, str] | None = None
        self.setWindowTitle("Post")
        self.resize(1180, 760)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # left: media ----------------------------------------------------------
        left = QWidget()
        left.setStyleSheet("background:#000;")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        self.media = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.media.setMinimumSize(420, 420)
        self.media.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.media.setStyleSheet("background:#000;")
        ll.addWidget(self.media, 1)
        nav = QHBoxLayout()
        nav.setContentsMargins(10, 0, 10, 8)
        self.btn_prev_post = QPushButton("◀ Prev post")
        self.btn_next_post = QPushButton("Next post ▶")
        self.btn_prev_m = QPushButton("‹")
        self.btn_next_m = QPushButton("›")
        self.dots = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.dots.setStyleSheet("color:white;background:transparent;font-size:16pt;")
        for b in (self.btn_prev_m, self.btn_next_m):
            b.setFixedWidth(40)
        nav.addWidget(self.btn_prev_post)
        nav.addStretch()
        nav.addWidget(self.btn_prev_m)
        nav.addWidget(self.dots)
        nav.addWidget(self.btn_next_m)
        nav.addStretch()
        nav.addWidget(self.btn_next_post)
        ll.addLayout(nav)
        root.addWidget(left, 3)

        # right: details ------------------------------------------------------
        right = QWidget()
        right.setMinimumWidth(400)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(14, 12, 14, 12)
        head = QHBoxLayout()
        self.avatar = QLabel()
        self.owner = ClickLabel()
        self.owner.setStyleSheet("font-weight:700;")
        self.owner.setCursor(Qt.CursorShape.PointingHandCursor)
        self.owner.clicked.connect(lambda: self._open_user(self.posts[self.i].owner))
        self.where = label("", "Muted")
        head.addWidget(self.avatar)
        v = QVBoxLayout()
        v.addWidget(self.owner)
        v.addWidget(self.where)
        head.addLayout(v)
        head.addStretch()
        self.kind_chip = chip("")
        head.addWidget(self.kind_chip)
        rl.addLayout(head)

        self.caption = QTextBrowser()
        self.caption.setMaximumHeight(110)
        self.caption.setOpenLinks(False)
        self.caption.anchorClicked.connect(self._link)
        rl.addWidget(self.caption)

        self.tabs = QTabWidget()
        self.comments_view = QTextBrowser()
        self.comments_view.setOpenLinks(False)
        self.comments_view.anchorClicked.connect(self._link)
        self.tabs.addTab(self.comments_view, "Comments")
        self.analysis = QWidget()
        self.tabs.addTab(scroll_wrap(self.analysis), "Emoji && sentiment")
        self.details = QTextBrowser()
        self.details.setOpenLinks(False)
        self.details.anchorClicked.connect(self._link)
        self.tabs.addTab(self.details, "Details")
        rl.addWidget(self.tabs, 1)

        actions = QHBoxLayout()
        self.btn_fav = QPushButton("♡")
        self.btn_fav.setObjectName("Flat")
        self.btn_fav.setToolTip("Local favourite (saved in this app only; does not like the post on Instagram)")
        self.btn_fav.setStyleSheet("font-size:16pt;")
        self.btn_fav.clicked.connect(self._toggle_fav)
        self.btn_dl = QPushButton("⬇ Download")
        self.btn_dl.clicked.connect(self._download)
        self.btn_open = QPushButton("Open on Instagram")
        self.btn_open.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.posts[self.i].permalink)))
        actions.addWidget(self.btn_fav)
        actions.addWidget(self.btn_dl)
        actions.addWidget(self.btn_open)
        actions.addStretch()
        rl.addLayout(actions)
        self.stats = label("", "Muted")
        rl.addWidget(self.stats)
        reply = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Add a reply… (select 'Reply' on a comment first)")
        self.input.returnPressed.connect(self._send_reply)
        self.btn_send = QPushButton("Post")
        self.btn_send.setObjectName("Primary")
        self.btn_send.clicked.connect(self._send_reply)
        reply.addWidget(self.input, 1)
        reply.addWidget(self.btn_send)
        rl.addLayout(reply)
        root.addWidget(right, 2)

        self.btn_prev_post.clicked.connect(lambda: self.go(-1))
        self.btn_next_post.clicked.connect(lambda: self.go(1))
        self.btn_prev_m.clicked.connect(lambda: self.frame(-1))
        self.btn_next_m.clicked.connect(lambda: self.frame(1))
        self.player = None
        self.media.installEventFilter(self)
        self._show()

    # navigation ---------------------------------------------------------------
    def keyPressEvent(self, e: QKeyEvent) -> None:  # noqa: N802
        k = e.key()
        if self.input.hasFocus() and k not in (Qt.Key.Key_Escape,):
            return super().keyPressEvent(e)
        if k == Qt.Key.Key_Left:
            self.go(-1)
        elif k == Qt.Key.Key_Right:
            self.go(1)
        elif k == Qt.Key.Key_Up:
            self.frame(-1)
        elif k == Qt.Key.Key_Down:
            self.frame(1)
        elif k == Qt.Key.Key_F:
            self.showNormal() if self.isFullScreen() else self.showFullScreen()
        else:
            super().keyPressEvent(e)

    def go(self, d: int) -> None:
        j = self.i + d
        if 0 <= j < len(self.posts):
            self.i, self.m, self.reply_to = j, 0, None
            self._show()

    def frame(self, d: int) -> None:
        n = len(self.posts[self.i].media)
        if 0 <= self.m + d < n:
            self.m += d
            self._render_media()

    def eventFilter(self, obj, ev):  # noqa: N802
        if obj is self.media and ev.type() == QEvent.Type.Resize:
            self._render_media()
        return super().eventFilter(obj, ev)

    # rendering ----------------------------------------------------------------
    @property
    def post(self) -> Post:
        return self.posts[self.i]

    def _render_media(self) -> None:
        p = self.post
        item = p.media[self.m] if p.media else MediaItem(seed=p.id)
        pm = media_pixmap(self.ctx, item, p.kind, on_ready=lambda _pm: self._render_media())
        self._stop_video()
        if item.is_video and item.seed.startswith("https://") and HAVE_VIDEO:
            self._play_video(item.seed)
            return
        self.media.setPixmap(pm.scaled(self.media.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation))
        n = len(p.media)
        self.dots.setText("  ".join("●" if k == self.m else "○" for k in range(n)) if n > 1 else "")
        self.btn_prev_m.setVisible(n > 1)
        self.btn_next_m.setVisible(n > 1)
        self.btn_prev_post.setEnabled(self.i > 0)
        self.btn_next_post.setEnabled(self.i < len(self.posts) - 1)

    def _play_video(self, url: str) -> None:
        self.video = QVideoWidget(self.media)
        self.video.setGeometry(self.media.rect())
        self.video.show()
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(QAudioOutput(self))
        self.player.setVideoOutput(self.video)
        self.player.setSource(QUrl(url))
        self.player.play()

    def _stop_video(self) -> None:
        if self.player is not None:
            self.player.stop()
            self.player.deleteLater()
            self.player = None
            self.video.deleteLater()

    def _show(self) -> None:
        p, acc = self.post, self.ctx.theme.accent_hex
        self.avatar.setPixmap(circle_crop(initials_avatar(p.owner, 38), 38))
        self.owner.setText(p.owner)
        self.where.setText(p.location or "")
        self.kind_chip.setText({"REEL": "Reel", "CAROUSEL": "Carousel", "VIDEO": "Video"}.get(p.kind, "Photo"))
        self.caption.setHtml(f"<b>{html.escape(p.owner)}</b> {richtext(p.caption, acc)}")
        self.stats.setText(f"♥ {fmt_count(p.likes)} likes   ·   💬 {fmt_count(p.comments_count)} comments   ·   "
                           + ago_long(p.timestamp))
        favs = set(self.ctx.db.get_setting("favorites", []))
        self.btn_fav.setText("♥" if p.id in favs else "♡")
        self.input.setPlaceholderText("Add a reply… (select 'Reply' on a comment first)")
        self.btn_send.setEnabled(self.ctx.registry.active.supports_write)
        self._render_media()
        self._render_details()
        self.comments_view.setHtml("<i>Loading comments…</i>")
        post = p

        def work():
            return self.ctx.registry.call("get_comments", post, fallback=False)

        run_async(work, lambda c, pid=post.id: self._comments_loaded(pid, c),
                  lambda e, pid=post.id: self._comments_failed(pid, e))

    def _comments_failed(self, pid: str, exc: Exception) -> None:
        if pid != self.post.id:
            return
        status = getattr(exc, "status", "PROVIDER UNAVAILABLE")
        self.comments = []
        self.comments_view.setHtml(f"<p><b>{html.escape(status)}</b><br>{html.escape(str(exc))}</p>")
        self._render_analysis()

    def _comments_loaded(self, pid: str, comments: list) -> None:
        if pid != self.post.id:
            return
        self.comments = comments
        acc = self.ctx.theme.accent_hex
        muted = self.ctx.theme.palette()["muted"]
        fg = self.ctx.theme.palette()["text"]

        def one(c, indent: int) -> str:
            likes = f" · {c.likes} likes" if c.likes else ""
            reply = f' · <a style="color:{acc};text-decoration:none" href="reply:{c.id}|{c.username}">Reply</a>' if indent == 0 else ""
            row = (f'<div style="margin-left:{indent}px;margin-bottom:8px">'
                   f'<a style="color:{fg};font-weight:700;text-decoration:none" href="user:{c.username}">'
                   f'{html.escape(c.username)}</a> {richtext(c.text, acc)}<br>'
                   f'<span style="color:{muted};font-size:8pt">{ago(c.timestamp)}{likes}{reply}</span></div>')
            return row + "".join(one(r, 28) for r in c.replies)

        n = len(an.flatten_comments(comments))
        self.comments_view.setHtml(
            f"<p style='color:{muted}'>{n} comment(s) retrieved "
            f"({self.post.comments_count if self.post.comments_count is not None else '?'} reported by the source)"
            f"</p>" + "".join(one(c, 0) for c in comments) if comments else "<p>No comments retrieved.</p>")
        self._render_analysis()

    def _render_analysis(self) -> None:
        for child in self.analysis.children():
            if isinstance(child, QWidget):
                child.deleteLater()
        lay = self.analysis.layout()
        if lay is None:
            lay = QVBoxLayout(self.analysis)
        while lay.count():
            it = lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        counts = an.emoji_counts(self.comments)
        groups = an.emoji_group_counts(counts)
        lay.addWidget(label(f"Counted from the {len(an.flatten_comments(self.comments))} comments retrieved — "
                            "not from Instagram's like button.", "Muted", wrap=True))
        g = BarChart("#F472B6")
        g.set_items(list(groups.items()))
        lay.addWidget(label("Reaction-style groups", "H2"))
        lay.addWidget(g)
        top = BarChart("#8B5CF6")
        top.set_items([(e, n) for e, n in list(counts.items())[:10]])
        lay.addWidget(label("Most-used emojis", "H2"))
        lay.addWidget(top)
        s = an.sentiment(self.comments)
        sb = BarChart("#22C55E")
        sb.set_items(list(s.items()))
        lay.addWidget(label("Sentiment (indicative, keyword-based)", "H2"))
        lay.addWidget(sb)
        tc = BarChart("#22D3EE")
        tc.set_items(an.top_commenters(self.comments, 6))
        lay.addWidget(label("Top commenters", "H2"))
        lay.addWidget(tc)
        lay.addStretch()

    def _render_details(self) -> None:
        p = self.post
        rate = an.engagement_rate(p, self.followers)
        rows = [("Type", p.kind), ("Posted", fmt_dt(p.timestamp)), ("Likes", fmt_count(p.likes)),
                ("Comments", fmt_count(p.comments_count)),
                ("Engagement rate", f"{rate}%" if rate is not None else "n/a"),
                ("Hashtags", ", ".join("#" + h for h in an.extract_hashtags(p.caption)) or "–"),
                ("Mentions", ", ".join("@" + m for m in an.extract_mentions(p.caption)) or "–"),
                ("Tagged", ", ".join("@" + t for t in p.tagged) or "–"),
                ("Location", p.location or "–"), ("Post ID", p.id)]
        self.details.setHtml("<table cellpadding=5>" + "".join(
            f"<tr><td><b>{k}</b></td><td>{html.escape(str(v))}</td></tr>" for k, v in rows) + "</table>")

    # actions --------------------------------------------------------------------
    def _open_user(self, user: str) -> None:
        self.ctx.open_profile.emit(user)
        self.accept()

    def _link(self, url: QUrl) -> None:
        s = url.toString()
        if s.startswith("user:"):
            self._open_user(s[5:])
        elif s.startswith("reply:"):
            cid, user = s[6:].split("|", 1)
            self.reply_to = (cid, user)
            self.input.setText(f"@{user} ")
            self.input.setPlaceholderText(f"Replying to @{user}")
            self.input.setFocus()

    def _toggle_fav(self) -> None:
        favs = list(self.ctx.db.get_setting("favorites", []))
        pid = self.post.id
        favs.remove(pid) if pid in favs else favs.append(pid)
        self.ctx.db.save_setting("favorites", favs)
        self.btn_fav.setText("♥" if pid in favs else "♡")

    def _download(self) -> None:
        p = self.post
        item = p.media[self.m] if p.media else MediaItem(seed=p.id)
        download_media(self.ctx, p.owner, f"{p.id}_{self.m}", item, p.kind, self)

    def _send_reply(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        if not self.reply_to:
            QMessageBox.information(self, "Choose a comment", "Click 'Reply' under a comment first.")
            return
        cid, user = self.reply_to
        if not self.ctx.is_demo:
            if QMessageBox.question(self, "Post public reply?", f"This will publish a reply to @{user} "
                                    "from your connected Instagram account.") != QMessageBox.StandardButton.Yes:
                return
        post = self.post

        def work():
            return self.ctx.registry.call("reply_to_comment", post, cid, text, fallback=False)

        def done(_):
            self.input.clear()
            self.reply_to = None
            self._show()

        run_async(work, done, lambda e: QMessageBox.warning(self, getattr(e, "status", "Reply failed"), str(e)))

    def done(self, r: int) -> None:
        self._stop_video()
        super().done(r)


# ---------------------------------------------------------------------------
class StoryViewer(QDialog):
    """Story player: segmented progress, tap zones, auto-advance across accounts."""

    DURATION_MS = 5000

    def __init__(self, ctx: AppContext, groups: list[tuple[str, list[Story]]], start: int = 0, parent=None):
        super().__init__(parent)
        self.ctx, self.groups, self.u, self.s = ctx, [g for g in groups if g[1]], start, 0
        self.paused, self.elapsed = False, 0
        self.setWindowTitle("Story")
        self.setFixedSize(440, 800)
        self.setStyleSheet("QDialog{background:#000;} QLabel{color:white;}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        self.bars_box = QHBoxLayout()
        self.bars_box.setSpacing(4)
        lay.addLayout(self.bars_box)
        head = QHBoxLayout()
        self.avatar = QLabel()
        self.name = QLabel()
        self.name.setStyleSheet("font-weight:700;color:white;")
        self.time = QLabel()
        self.time.setStyleSheet("color:#bbb;")
        self.pause_lbl = QLabel("")
        close = QPushButton("✕")
        close.setObjectName("Flat")
        close.setStyleSheet("color:white;font-size:14pt;")
        close.clicked.connect(self.accept)
        head.addWidget(self.avatar)
        head.addWidget(self.name)
        head.addWidget(self.time)
        head.addStretch()
        head.addWidget(self.pause_lbl)
        head.addWidget(close)
        lay.addLayout(head)
        self.media = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.media.setStyleSheet("background:#111;border-radius:12px;")
        self.media.setMinimumHeight(560)
        self.media.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.media.installEventFilter(self)
        lay.addWidget(self.media, 1)
        self.meta = QLabel("")
        self.meta.setWordWrap(True)
        lay.addWidget(self.meta)
        self.chips = QHBoxLayout()
        lay.addLayout(self.chips)
        foot = QHBoxLayout()
        self.btn_dl = QPushButton("⬇ Save")
        self.btn_dl.clicked.connect(self._download)
        foot.addWidget(label("← → navigate · Space pause · Esc close", "Muted"))
        foot.addStretch()
        foot.addWidget(self.btn_dl)
        lay.addLayout(foot)
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._tick)
        self._load()
        self.timer.start()

    @property
    def stories(self) -> list[Story]:
        return self.groups[self.u][1]

    def _load(self) -> None:
        user, stories = self.groups[self.u]
        st = stories[self.s]
        self.elapsed = 0
        self.avatar.setPixmap(circle_crop(initials_avatar(user, 34), 34))
        self.name.setText(user)
        self.time.setText(ago(st.timestamp))
        while self.bars_box.count():
            w = self.bars_box.takeAt(0).widget()
            if w:
                w.deleteLater()
        self.bars = []
        for k in range(len(stories)):
            b = QProgressBar()
            b.setRange(0, 1000)
            b.setTextVisible(False)
            b.setFixedHeight(4)
            b.setValue(1000 if k < self.s else 0)
            self.bars_box.addWidget(b)
            self.bars.append(b)
        pm = media_pixmap(self.ctx, st.media, "STORY", on_ready=lambda _p: self._render(st))
        self._render(st, pm)
        extra = " · ".join(x for x in (f"📍 {st.location}" if st.location else "",
                                       f"🎵 {st.music}" if st.music else "",
                                       "▶ video" if st.media.is_video else "") if x)
        self.meta.setText(extra)
        while self.chips.count():
            w = self.chips.takeAt(0).widget()
            if w:
                w.deleteLater()
        for m in st.mentions:
            b = QPushButton(f"@{m}")
            b.clicked.connect(lambda _=False, u=m: (self.ctx.open_profile.emit(u), self.accept()))
            self.chips.addWidget(b)
        self.chips.addStretch()
        seen = set(self.ctx.db.get_setting("seen_stories", []))
        seen.add(st.id)
        self.ctx.db.save_setting("seen_stories", sorted(seen)[-2000:])

    def _render(self, st: Story, pm: QPixmap | None = None) -> None:
        pm = pm or media_pixmap(self.ctx, st.media, "STORY")
        self.media.setPixmap(pm.scaled(self.media.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation))

    def _tick(self) -> None:
        if self.paused:
            return
        self.elapsed += self.timer.interval()
        self.bars[self.s].setValue(min(1000, int(1000 * self.elapsed / self.DURATION_MS)))
        if self.elapsed >= self.DURATION_MS:
            self.next()

    def next(self) -> None:
        if self.s + 1 < len(self.stories):
            self.s += 1
        elif self.u + 1 < len(self.groups):
            self.u, self.s = self.u + 1, 0
        else:
            self.accept()
            return
        self._load()

    def prev(self) -> None:
        if self.s > 0:
            self.s -= 1
        elif self.u > 0:
            self.u -= 1
            self.s = 0
        self._load()

    def eventFilter(self, obj, ev):  # noqa: N802
        if obj is self.media and ev.type() == QEvent.Type.Resize:
            self._render(self.stories[self.s])
        if obj is self.media and ev.type() == QEvent.Type.MouseButtonPress:
            x = ev.position().x() / max(1, self.media.width())
            self.prev() if x < 0.3 else self.next()
            return True
        return super().eventFilter(obj, ev)

    def keyPressEvent(self, e: QKeyEvent) -> None:  # noqa: N802
        if e.key() == Qt.Key.Key_Right:
            self.next()
        elif e.key() == Qt.Key.Key_Left:
            self.prev()
        elif e.key() == Qt.Key.Key_Space:
            self.paused = not self.paused
            self.pause_lbl.setText("⏸" if self.paused else "")
        else:
            super().keyPressEvent(e)

    def _download(self) -> None:
        st = self.stories[self.s]
        download_media(self.ctx, st.owner, st.id, st.media, "STORY", self)

    def done(self, r: int) -> None:
        self.timer.stop()
        super().done(r)
