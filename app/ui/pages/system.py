"""Provider manager, settings, notifications and diagnostics."""

from __future__ import annotations

import platform
import sys

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.core import secrets
from app.ui.pages.base import Page
from app.ui.pages.tools import open_path
from app.ui.theme import ACCENTS
from app.ui.widgets import Panel, chip, fill_table, label, make_table, scroll_wrap
from app.ui.workers import run_async
from app.utils import fmt_dt

EXPORT_HELP = (
    "<b>How to get a complete 587-of-587 list for your own account</b><br>"
    "Instagram → Settings → <i>Accounts Center</i> → <i>Your information and permissions</i> → "
    "<i>Download your information</i> → choose <i>Followers and following</i>, format <b>JSON</b>. "
    "Then use <i>Import Instagram data export…</i> on the Followers &amp; Following page and select the .zip. "
    "Each re-import becomes a snapshot, so changes between exports are detected."
)


class ProvidersPage(Page):
    key = "providers"
    title = "Provider manager"
    subtitle = "Data sources, what each can and cannot provide, and their health. Fallback never uses demo data."

    def __init__(self, ctx):
        super().__init__(ctx)
        inner = QWidget()
        self.lay = QVBoxLayout(inner)
        self.lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.root.addWidget(scroll_wrap(inner), 1)
        self.health_labels: dict[str, object] = {}

    def on_show(self) -> None:
        super().on_show()
        while self.lay.count():
            w = self.lay.takeAt(0).widget()
            if w:
                w.deleteLater()
        reg = self.ctx.registry
        for name, prov in reg.providers.items():
            panel = Panel(prov.label, prov.description)
            head = QHBoxLayout()
            if reg.active_name == name:
                head.addWidget(chip("ACTIVE", "ChipOk"))
            use = QPushButton("Use this provider")
            use.setEnabled(reg.active_name != name)
            use.clicked.connect(lambda _=False, n=name: self._use(n))
            en = QCheckBox("Enabled")
            en.setChecked(reg.enabled(name))
            en.toggled.connect(lambda v, n=name: self.ctx.db.save_setting(f"provider_enabled_{n}", v))
            test = QPushButton("Check health")
            hl = label("", "Muted")
            test.clicked.connect(lambda _=False, n=name, h=hl: self._health(n, h))
            for w in (use, en, test, hl):
                head.addWidget(w)
            head.addStretch()
            panel.body.addLayout(head)
            t = make_table(["Feature", "Status", "Note"])
            caps = prov.capabilities()
            fill_table(t, [[c.label, c.status, c.note] for c in caps])
            colors = {"AVAILABLE": "ok", "PARTIALLY AVAILABLE": "warn", "PERMISSION REQUIRED": "warn"}
            pal = self.ctx.theme.palette()
            for r, c in enumerate(caps):
                t.item(r, 1).setForeground(QColor(pal[colors.get(c.status, "bad")]))
            t.setFixedHeight(40 + 30 * len(caps))
            panel.body.addWidget(t)
            if name == "graph":
                panel.body.addWidget(self._graph_form())
            self.lay.addWidget(panel)

        guide = Panel("Instagram data export (recommended for complete lists)")
        guide.body.addWidget(label(EXPORT_HELP, wrap=True))
        self.lay.addWidget(guide)
        addp = Panel("Adding another provider")
        addp.body.addWidget(label(
            "Create a class in app/providers/ that subclasses Provider, implement only the methods the source "
            "genuinely supports, raise ProviderError with an availability status for the rest, and register it in "
            "app/providers/registry.py. See docs/PROVIDERS.md. Only integrate sources you are authorised to use and "
            "that comply with Instagram's terms.", wrap=True))
        self.lay.addWidget(addp)

    def _use(self, name: str) -> None:
        self.ctx.db.save_setting("active_provider", name)
        self.ctx.invalidate()
        self.ctx.navigate.emit("providers")
        self.on_show()

    def _health(self, name: str, lbl) -> None:
        lbl.setText("checking…")

        def done(h):
            lbl.setText(f"{'✔' if h.ok else '✖'} {h.message} · {h.ms} ms")

        run_async(lambda: self.ctx.registry.check(name), done, lambda e: lbl.setText(str(e)))

    def _graph_form(self) -> QWidget:
        w = QWidget()
        w.setObjectName("Transparent")
        form = QFormLayout(w)
        self.token = QLineEdit(secrets.get_secret("graph_token"))
        self.token.setEchoMode(QLineEdit.EchoMode.Password)
        self.token.setPlaceholderText("Access token (stored in Windows Credential Manager)")
        self.uid = QLineEdit(str(self.ctx.db.get_setting("graph_user_id", "")))
        self.uname = QLineEdit(str(self.ctx.db.get_setting("graph_username", "")))
        self.ver = QLineEdit(str(self.ctx.db.get_setting("graph_version", "v23.0")))
        form.addRow("Access token", self.token)
        form.addRow("Instagram user ID", self.uid)
        form.addRow("Your username", self.uname)
        form.addRow("API version", self.ver)
        save = QPushButton("Save && test connection")
        save.setObjectName("Primary")
        save.clicked.connect(self._save_graph)
        form.addRow(save)
        form.addRow(label("Requires an Instagram Business/Creator account linked to a Meta app, with the permissions "
                          "instagram_basic, instagram_manage_comments and instagram_manage_insights. The token is "
                          "never written to the database, logs or exports.", "Muted", wrap=True))
        return w

    def _save_graph(self) -> None:
        persisted = secrets.set_secret("graph_token", self.token.text().strip())
        self.ctx.db.save_setting("graph_user_id", self.uid.text().strip())
        self.ctx.db.save_setting("graph_username", self.uname.text().strip().lstrip("@"))
        self.ctx.db.save_setting("graph_version", self.ver.text().strip() or "v23.0")
        self.ctx.registry.reload()

        def done(h):
            msg = "Connected." if h.ok else f"Not connected: {h.message}"
            if not persisted:
                msg += "\n\nNo OS keyring available: the token is kept for this session only."
            QMessageBox.information(self, "Graph API", msg)
            self.on_show()

        run_async(lambda: self.ctx.registry.check("graph"), done, lambda e: QMessageBox.warning(self, "Error", str(e)))


class SettingsPage(Page):
    key = "settings"
    title = "Settings"
    subtitle = "Appearance, background, privacy, data and maintenance."

    def __init__(self, ctx):
        super().__init__(ctx)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        t = ctx.theme

        ap = Panel("Appearance & personalisation")
        f = QFormLayout()
        self.mode = self._combo(["Dark", "Light"], t.mode)
        self.accent = self._combo(list(ACCENTS), t.accent)
        self.card = self._combo(["Glass", "Solid", "Minimal"], t.card_style)
        self.density = self._combo(["Comfortable", "Compact"], t.density)
        self.bg = self._combo(["Gradient", "Solid", "Image"], t.background)
        pick = QPushButton("Choose wallpaper…")
        pick.clicked.connect(self._wallpaper)
        self.dim = QSlider(Qt.Orientation.Horizontal)
        self.dim.setRange(0, 90)
        self.dim.setValue(t.background_dim)
        self.dim.valueChanged.connect(self._apply)
        self.anim = QCheckBox("Smooth animations (turn off for reduced motion)")
        self.anim.setChecked(t.animations)
        self.anim.toggled.connect(self._apply)
        self.compact_sb = QCheckBox("Compact sidebar (icons only)")
        self.compact_sb.setChecked(t.sidebar_compact)
        self.compact_sb.toggled.connect(self._apply)
        for lbl, w in (("Theme", self.mode), ("Accent colour", self.accent), ("Card style", self.card),
                       ("Density", self.density), ("Background", self.bg), ("Wallpaper", pick),
                       ("Wallpaper darkening", self.dim), ("", self.anim), ("", self.compact_sb)):
            f.addRow(lbl, w)
        ap.body.addLayout(f)
        lay.addWidget(ap)

        beh = Panel("Behaviour")
        self.tray = QCheckBox("Keep running in the system tray when the window is closed (needed for background monitoring)")
        self.tray.setChecked(bool(ctx.db.get_setting("close_to_tray", True)))
        self.tray.toggled.connect(lambda v: ctx.db.save_setting("close_to_tray", v))
        self.desktop = QCheckBox("Show Windows desktop notifications")
        self.desktop.setChecked(bool(ctx.db.get_setting("desktop_notifications", True)))
        self.desktop.toggled.connect(lambda v: ctx.db.save_setting("desktop_notifications", v))
        self.autob = QCheckBox("Automatic database backup on start (keeps the 10 newest)")
        self.autob.setChecked(bool(ctx.db.get_setting("auto_backup", True)))
        self.autob.toggled.connect(lambda v: ctx.db.save_setting("auto_backup", v))
        self.startup = QCheckBox("Start with Windows (minimised to tray)")
        self.startup.setEnabled(sys.platform.startswith("win"))
        self.startup.setChecked(bool(ctx.db.get_setting("start_with_windows", False)))
        self.startup.toggled.connect(self._startup)
        for w in (self.tray, self.desktop, self.autob, self.startup):
            beh.body.addWidget(w)
        lay.addWidget(beh)

        pr = Panel("Privacy & data", f"Data folder: {ctx.data_dir}")
        row = QHBoxLayout()
        for text, fn in (("Open data folder", lambda: open_path(ctx.data_dir)), ("Clear search history", self._clear_hist),
                         ("Clear image cache", self._clear_cache)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        row.addStretch()
        pr.body.addLayout(row)
        row2 = QHBoxLayout()
        self.del_box = QComboBox()
        delete = QPushButton("Delete all stored data for this profile")
        delete.clicked.connect(self._delete_profile)
        row2.addWidget(self.del_box)
        row2.addWidget(delete)
        row2.addStretch()
        pr.body.addLayout(row2)
        pr.body.addWidget(label("No Instagram password is ever requested. API tokens live in Windows Credential "
                                "Manager, not in this app's database. Nothing is sent anywhere except to the provider "
                                "you enable.", "Muted", wrap=True))
        lay.addWidget(pr)
        self.root.addWidget(scroll_wrap(inner), 1)

    def _combo(self, items, current):
        c = QComboBox()
        c.addItems(items)
        c.setCurrentText(current)
        c.currentTextChanged.connect(self._apply)
        return c

    def on_show(self) -> None:
        super().on_show()
        self.del_box.clear()
        names = sorted({r["username"] for r in self.ctx.db.list_profiles()} | {s["profile"] for s in self.ctx.db.list_snapshots()}
                       | {self.ctx.profile})
        self.del_box.addItems(names)

    def _apply(self, *_a) -> None:
        t = self.ctx.theme
        t.mode, t.accent, t.card_style = self.mode.currentText(), self.accent.currentText(), self.card.currentText()
        t.density, t.background = self.density.currentText(), self.bg.currentText()
        t.background_dim, t.animations, t.sidebar_compact = self.dim.value(), self.anim.isChecked(), self.compact_sb.isChecked()
        self.ctx.save_theme()

    def _wallpaper(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose wallpaper", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if path:
            self.ctx.theme.background_image = path
            self.bg.setCurrentText("Image")
            self._apply()

    def _startup(self, on: bool) -> None:
        self.ctx.db.save_setting("start_with_windows", on)
        try:
            import winreg  # type: ignore[import-not-found]

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_SET_VALUE)
            if on:
                winreg.SetValueEx(key, "InstagramResearchSuite", 0, winreg.REG_SZ, f'"{sys.executable}" --minimized')
            else:
                try:
                    winreg.DeleteValue(key, "InstagramResearchSuite")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Startup", f"Could not change the startup setting: {exc}")

    def _clear_hist(self) -> None:
        self.ctx.db.clear_search_history()
        self.ctx.toast.emit("Cleared", "Search history removed.")

    def _clear_cache(self) -> None:
        n = 0
        for f in (self.ctx.data_dir / "cache").glob("*.img"):
            f.unlink(missing_ok=True)
            n += 1
        self.ctx.toast.emit("Cleared", f"{n} cached images removed. Saved downloads are untouched.")

    def _delete_profile(self) -> None:
        u = self.del_box.currentText()
        if u and QMessageBox.question(self, "Delete data", f"Permanently delete snapshots, events, mentions and "
                                      f"monitors for @{u}? Downloaded files stay on disk.") == QMessageBox.StandardButton.Yes:
            self.ctx.db.delete_profile_data(u)
            self.ctx.data_changed.emit()
            self.on_show()


class NotificationsPage(Page):
    key = "notifications"
    title = "Notifications"
    subtitle = "Everything the monitoring engine has told you."

    def __init__(self, ctx):
        super().__init__(ctx)
        bar = QHBoxLayout()
        mark = QPushButton("Mark all as read")
        mark.clicked.connect(lambda: (ctx.db.mark_notifications_read(), self.on_show(), ctx.data_changed.emit()))
        bar.addWidget(mark)
        bar.addStretch()
        self.root.addLayout(bar)
        self.table = make_table(["When", "Type", "Title", "Details", "Read"])
        self.root.addWidget(self.table, 1)

    def on_show(self) -> None:
        super().on_show()
        fill_table(self.table, [[fmt_dt(n["created_at"]), n["kind"], n["title"], n["body"], "" if not n["is_read"] else "✓"]
                                for n in self.ctx.db.list_notifications()])


class LogsPage(Page):
    key = "logs"
    title = "Logs & diagnostics"
    subtitle = "Application log, database health and environment details for troubleshooting."

    def __init__(self, ctx):
        super().__init__(ctx)
        bar = QHBoxLayout()
        for text, fn in (("Refresh", self.on_show), ("Check database integrity", self._integrity),
                         ("Optimise database", self._vacuum), ("Open logs folder", lambda: open_path(ctx.data_dir / "logs"))):
            b = QPushButton(text)
            b.clicked.connect(fn)
            bar.addWidget(b)
        bar.addStretch()
        self.root.addLayout(bar)
        self.info = label("", "Muted", wrap=True)
        self.root.addWidget(self.info)
        self.view = QPlainTextEdit()
        self.view.setReadOnly(True)
        self.view.setStyleSheet("font-family: Consolas, monospace; font-size: 9pt;")
        self.root.addWidget(self.view, 1)

    def on_show(self) -> None:
        super().on_show()
        self.info.setText(f"Version {__version__} · Python {platform.python_version()} · PySide6 {pyside_version} · "
                          f"{platform.platform()} · data: {self.ctx.data_dir}")
        log = self.ctx.data_dir / "logs" / "application.log"
        self.view.setPlainText("\n".join(log.read_text(encoding="utf-8", errors="replace").splitlines()[-400:])
                               if log.exists() else "No log yet.")
        self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().maximum())

    def _integrity(self) -> None:
        QMessageBox.information(self, "Integrity check", f"Result: {self.ctx.db.integrity_check()}")

    def _vacuum(self) -> None:
        self.ctx.db.vacuum()
        QMessageBox.information(self, "Database", "Optimised.")
