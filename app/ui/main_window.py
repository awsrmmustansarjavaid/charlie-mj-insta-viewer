"""Main window: sidebar, backdrop, command palette, toasts, tray."""

from __future__ import annotations

import logging

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QIcon,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenu,
    QPushButton,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.core.resources import resource_path
from app.ui.context import AppContext
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.engagement import EngagementPage
from app.ui.pages.feed import FeedPage
from app.ui.pages.followers import FollowersPage
from app.ui.pages.history import SnapshotsPage, TimelinePage
from app.ui.pages.insights import InsightsPage
from app.ui.pages.mentions import MentionsPage
from app.ui.pages.monitor import MonitorPage
from app.ui.pages.profile import ProfilePage
from app.ui.pages.system import LogsPage, NotificationsPage, ProvidersPage, SettingsPage
from app.ui.pages.tools import ComparePage, ExportPage, LibraryPage
from app.ui.scheduler import MonitorScheduler
from app.ui.theme import build_stylesheet
from app.ui.widgets import chip

log = logging.getLogger(__name__)

NAV = [
    ("OVERVIEW", [("dashboard", "▣", "Dashboard")]),
    ("INSTAGRAM EXPERIENCE", [("feed", "⌂", "Home feed & stories"), ("profile", "◉", "Profile explorer")]),
    ("TRACKING", [("followers", "⇄", "Followers & following"), ("insights", "◔", "Account insights"),
                  ("snapshots", "⧉", "Snapshots & compare"), ("timeline", "⏱", "Activity timeline")]),
    ("ENGAGEMENT", [("engagement", "♡", "Posts & comments"), ("mentions", "@", "Mentions & tags")]),
    ("MONITORING", [("monitor", "◎", "Monitoring"), ("notifications", "🔔", "Notifications")]),
    ("TOOLS", [("compare", "⚖", "Compare profiles"), ("library", "▤", "Library & downloads"),
               ("export", "⇪", "Export & backup")]),
    ("SYSTEM", [("providers", "⛁", "Provider manager"), ("settings", "⚙", "Settings"), ("logs", "☰", "Logs & diagnostics")]),
]


def app_icon() -> QIcon:
    path = resource_path("assets/icon.png")
    if path.exists():
        return QIcon(str(path))
    pm = QPixmap(128, 128)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    g = QLinearGradient(0, 128, 128, 0)
    for pos, col in ((0, "#feda75"), (0.4, "#d62976"), (1, "#4f5bd5")):
        g.setColorAt(pos, QColor(col))
    p.setBrush(QBrush(g))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(4, 4, 120, 120), 30, 30)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QColor("white"))
    p.drawRoundedRect(QRectF(30, 30, 68, 68), 20, 20)
    p.drawEllipse(QPointF(64, 64), 17, 17)
    p.end()
    return QIcon(pm)


class Backdrop(QWidget):
    """Paints the gradient / solid / wallpaper behind everything."""

    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self._img: QPixmap | None = None
        self._img_path = ""

    def paintEvent(self, _e):  # noqa: N802
        t = self.ctx.theme
        p = QPainter(self)
        pal = t.palette()
        p.fillRect(self.rect(), QColor(pal["bg"]))
        if t.background == "Gradient" and t.dark:
            rg = QRadialGradient(self.width() * 0.85, self.height() * 0.05, self.width() * 0.7)
            rg.setColorAt(0, QColor(139, 92, 246, 80))
            rg.setColorAt(1, QColor(139, 92, 246, 0))
            p.fillRect(self.rect(), rg)
            rg2 = QRadialGradient(self.width() * 0.1, self.height() * 0.95, self.width() * 0.6)
            rg2.setColorAt(0, QColor(34, 211, 238, 50))
            rg2.setColorAt(1, QColor(34, 211, 238, 0))
            p.fillRect(self.rect(), rg2)
        elif t.background == "Gradient":
            g = QLinearGradient(0, 0, self.width(), self.height())
            g.setColorAt(0, QColor("#EEF1FF"))
            g.setColorAt(1, QColor("#F8EEFF"))
            p.fillRect(self.rect(), g)
        elif t.background == "Image" and t.background_image:
            if self._img_path != t.background_image:
                self._img, self._img_path = QPixmap(t.background_image), t.background_image
            if self._img and not self._img.isNull():
                s = self._img.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                     Qt.TransformationMode.SmoothTransformation)
                p.drawPixmap((self.width() - s.width()) // 2, (self.height() - s.height()) // 2, s)
                shade = QColor(0, 0, 0, int(255 * t.background_dim / 100)) if t.dark else \
                    QColor(255, 255, 255, int(255 * t.background_dim / 100))
                p.fillRect(self.rect(), shade)


class Toast(QLabel):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setMaximumWidth(380)
        self.setStyleSheet("background:#1f2a44;color:white;border:1px solid #8B5CF6;border-radius:10px;padding:10px 14px;")
        self.hide()
        self.timer = QTimer(self, singleShot=True, interval=4500)
        self.timer.timeout.connect(self.hide)

    def show_message(self, title: str, body: str) -> None:
        self.setText(f"<b>{title}</b><br>{body}" if body else f"<b>{title}</b>")
        self.adjustSize()
        self.move(self.parent().width() - self.width() - 24, self.parent().height() - self.height() - 24)
        self.raise_()
        self.show()
        self.timer.start()


class CommandPalette(QDialog):
    def __init__(self, win: MainWindow):
        super().__init__(win)
        self.win = win
        self.setWindowTitle("Command palette")
        self.setMinimumSize(520, 420)
        lay = QVBoxLayout(self)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Go to a page, or type a username to open its profile…")
        self.edit.textChanged.connect(self._fill)
        self.edit.returnPressed.connect(self._run)
        self.list = QListWidget()
        self.list.itemActivated.connect(lambda _i: self._run())
        lay.addWidget(self.edit)
        lay.addWidget(self.list)
        self._fill("")

    def _fill(self, text: str) -> None:
        self.list.clear()
        q = text.strip().lower()
        if q:
            self.list.addItem(f"Open profile @{q.lstrip('@')}")
            self.list.item(0).setData(Qt.ItemDataRole.UserRole, ("profile", q.lstrip("@")))
        for _sec, items in NAV:
            for key, icon, title in items:
                if not q or q in title.lower():
                    self.list.addItem(f"{icon}  {title}")
                    self.list.item(self.list.count() - 1).setData(Qt.ItemDataRole.UserRole, ("page", key))
        if not q:
            for u in self.win.ctx.db.list_searches(6):
                self.list.addItem(f"↺  @{u}")
                self.list.item(self.list.count() - 1).setData(Qt.ItemDataRole.UserRole, ("profile", u))
        self.list.setCurrentRow(0)

    def _run(self) -> None:
        item = self.list.currentItem()
        if not item:
            return
        kind, val = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
        if kind == "page":
            self.win.show_page(val)
        else:
            self.win.ctx.open_profile.emit(val)


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext, start_minimized: bool = False):
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle(f"Instagram Research Suite {__version__}")
        self.setWindowIcon(app_icon())
        self.resize(1480, 920)
        self.setMinimumSize(1100, 700)
        self.scheduler = MonitorScheduler(ctx)

        central = Backdrop(ctx)
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_sidebar())
        right = QVBoxLayout()
        right.setSpacing(0)
        right.addWidget(self._build_topbar())
        self.stack = QStackedWidget()
        right.addWidget(self.stack, 1)
        outer.addLayout(right, 1)

        self.pages: dict[str, QWidget] = {}
        for page in (DashboardPage(ctx), FeedPage(ctx), ProfilePage(ctx), FollowersPage(ctx), InsightsPage(ctx),
                     SnapshotsPage(ctx), TimelinePage(ctx), EngagementPage(ctx), MentionsPage(ctx),
                     MonitorPage(ctx, self.scheduler), NotificationsPage(ctx), ComparePage(ctx), LibraryPage(ctx),
                     ExportPage(ctx), ProvidersPage(ctx), SettingsPage(ctx), LogsPage(ctx)):
            self.pages[page.key] = page
            self.stack.addWidget(page)

        self.toast = Toast(central)
        ctx.toast.connect(self.toast.show_message)
        ctx.navigate.connect(self.show_page)
        ctx.profile_changed.connect(self._profile_changed)
        ctx.data_changed.connect(self._refresh_bell)
        ctx.theme_changed.connect(self.apply_theme)
        self.scheduler.cycle_finished.connect(self._cycle_done)

        QShortcut(QKeySequence("Ctrl+K"), self, activated=lambda: CommandPalette(self).exec())
        QShortcut(QKeySequence("F11"), self, activated=lambda: self.showNormal() if self.isFullScreen()
                  else self.showFullScreen())
        QShortcut(QKeySequence("Ctrl+R"), self, activated=lambda: self.pages[self.current].on_show())
        for i, key in enumerate(("dashboard", "feed", "profile", "followers", "engagement", "mentions", "monitor"), 1):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, activated=lambda k=key: self.show_page(k))

        self.tray = self._build_tray()
        self.apply_theme()
        self.current = "dashboard"
        self.show_page("dashboard")
        self._refresh_bell()
        if start_minimized and self.tray:
            QTimer.singleShot(0, self.hide)

    # -- construction -----------------------------------------------------------
    def _build_sidebar(self) -> QWidget:
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar_lay = QVBoxLayout(self.sidebar)
        self.sidebar_lay.setContentsMargins(10, 14, 10, 10)
        self.sidebar_lay.setSpacing(2)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.nav_buttons: dict[str, QPushButton] = {}
        self.section_labels: list[QLabel] = []
        brand = QLabel("◎  Instagram Research")
        brand.setObjectName("Brand")
        self.brand = brand
        self.sidebar_lay.addWidget(brand)
        sub = QLabel("Suite · Windows portable")
        sub.setObjectName("Muted")
        self.sub = sub
        self.sidebar_lay.addWidget(sub)
        for section, items in NAV:
            sl = QLabel(section)
            sl.setObjectName("Section")
            self.section_labels.append(sl)
            self.sidebar_lay.addWidget(sl)
            for key, icon, title in items:
                b = QPushButton(f"{icon}   {title}".replace("&", "&&"))
                b.setObjectName("Nav")
                b.setCheckable(True)
                b.setProperty("full", f"{icon}   {title}".replace("&", "&&"))
                b.setProperty("icon_only", icon)
                b.setToolTip(title)
                b.clicked.connect(lambda _=False, k=key: self.show_page(k))
                self.group.addButton(b)
                self.nav_buttons[key] = b
                self.sidebar_lay.addWidget(b)
        self.sidebar_lay.addStretch()
        self.acct = QLabel("")
        self.acct.setObjectName("Muted")
        self.sidebar_lay.addWidget(self.acct)
        self.sidebar.setFixedWidth(250)
        return self.sidebar

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("Transparent")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(26, 12, 26, 0)
        pal = QPushButton("🔍  Search or jump to…   Ctrl+K")
        pal.setMinimumWidth(320)
        pal.setStyleSheet("text-align:left;")
        pal.clicked.connect(lambda: CommandPalette(self).exec())
        self.profile_chip = chip("")
        self.provider_chip = chip("")
        self.bell = QPushButton("🔔")
        self.bell.setObjectName("Flat")
        self.bell.clicked.connect(lambda: self.show_page("notifications"))
        lay.addWidget(pal)
        lay.addStretch()
        lay.addWidget(self.profile_chip)
        lay.addWidget(self.provider_chip)
        lay.addWidget(self.bell)
        return bar

    def _build_tray(self) -> QSystemTrayIcon | None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return None
        tray = QSystemTrayIcon(app_icon(), self)
        menu = QMenu()
        show = QAction("Open Instagram Research Suite", self)
        show.triggered.connect(self._restore)
        run = QAction("Run due monitoring checks now", self)
        run.triggered.connect(self.scheduler.tick)
        quit_ = QAction("Quit", self)
        quit_.triggered.connect(self._quit)
        for a in (show, run, quit_):
            menu.addAction(a)
        tray.setContextMenu(menu)
        tray.activated.connect(lambda r: self._restore() if r == QSystemTrayIcon.ActivationReason.Trigger else None)
        tray.setToolTip("Instagram Research Suite")
        tray.show()
        return tray

    # -- behaviour ----------------------------------------------------------------
    def show_page(self, key: str) -> None:
        page = self.pages.get(key)
        if not page:
            return
        self.current = key
        self.stack.setCurrentWidget(page)
        if key in self.nav_buttons:
            self.nav_buttons[key].setChecked(True)
        else:
            self.group.setExclusive(False)
            for b in self.nav_buttons.values():
                b.setChecked(False)
            self.group.setExclusive(True)
        page.on_show()
        self._profile_changed("")

    def _profile_changed(self, _u: str) -> None:
        self.profile_chip.setText(f"@{self.ctx.profile}")
        self.provider_chip.setText(("DEMO · " if self.ctx.is_demo else "") + self.ctx.provider_label)
        self.provider_chip.setObjectName("ChipWarn" if self.ctx.is_demo else "ChipOk")
        self.provider_chip.style().unpolish(self.provider_chip)
        self.provider_chip.style().polish(self.provider_chip)
        self.acct.setText(f"Active profile\n@{self.ctx.profile}")

    def _refresh_bell(self) -> None:
        n = self.ctx.db.unread_count()
        self.bell.setText(f"🔔 {n}" if n else "🔔")

    def apply_theme(self) -> None:
        t = self.ctx.theme
        app = QApplication.instance()
        app.setStyleSheet(build_stylesheet(t))
        pal = QPalette(app.palette())
        text = QColor(t.palette()["text"])
        for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
            pal.setColor(role, text)
        pal.setColor(QPalette.ColorRole.Link, QColor(t.accent_hex))
        pal.setColor(QPalette.ColorRole.LinkVisited, QColor(t.accent_hex))
        app.setPalette(pal)
        compact = t.sidebar_compact
        self.sidebar.setFixedWidth(64 if compact else 250)
        for b in self.nav_buttons.values():
            b.setText(b.property("icon_only") if compact else b.property("full"))
        for w in (self.brand, self.sub, self.acct, *self.section_labels):
            w.setVisible(not compact)
        self.centralWidget().update()
        self._profile_changed("")

    def _cycle_done(self, profile: str, status: str, changes: list) -> None:
        self._refresh_bell()
        if changes:
            body = "\n".join(changes[:5])
            self.ctx.toast.emit(f"Monitoring: @{profile}", body)
            if self.tray and self.ctx.db.get_setting("desktop_notifications", True):
                self.tray.showMessage(f"@{profile}: {len(changes)} change(s) detected", body,
                                      QSystemTrayIcon.MessageIcon.Information, 6000)
        elif status == "error":
            self.ctx.toast.emit("Monitoring problem", f"The check for @{profile} failed. See Notifications.")
        if self.current in ("dashboard", "timeline", "notifications", "monitor"):
            self.pages[self.current].on_show()

    def _restore(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _quit(self) -> None:
        self._really_quit = True
        QApplication.quit()

    def closeEvent(self, e):  # noqa: N802
        if self.tray and self.ctx.db.get_setting("close_to_tray", True) and not getattr(self, "_really_quit", False):
            e.ignore()
            self.hide()
            if not self.ctx.db.get_setting("tray_hint_shown", False):
                self.tray.showMessage("Still running", "Monitoring continues in the tray. Right-click the icon to quit.",
                                      QSystemTrayIcon.MessageIcon.Information, 5000)
                self.ctx.db.save_setting("tray_hint_shown", True)
            return
        self.scheduler.timer.stop()
        e.accept()
