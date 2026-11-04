"""Base class for all pages."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from app.ui.context import AppContext
from app.ui.widgets import chip, label


class Page(QWidget):
    key = ""
    title = ""
    subtitle = ""

    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self.setObjectName("Page")
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(26, 20, 26, 16)
        self.root.setSpacing(12)
        head = QHBoxLayout()
        box = QVBoxLayout()
        box.setSpacing(0)
        box.addWidget(label(self.title, "PageTitle"))
        if self.subtitle:
            box.addWidget(label(self.subtitle, "Muted", wrap=True))
        head.addLayout(box, 1)
        self.header_right = QHBoxLayout()
        head.addLayout(self.header_right)
        self.root.addLayout(head)
        self.banner = QFrame()
        self.banner.setObjectName("Banner")
        bl = QHBoxLayout(self.banner)
        bl.setContentsMargins(12, 6, 12, 6)
        bl.addWidget(label("Demo mode — all accounts, posts and numbers on screen are fictional sample data. "
                           "Connect a real source in Provider Manager.", "Muted", wrap=True))
        self.root.addWidget(self.banner)
        ctx.theme_changed.connect(self.on_theme)

    def on_show(self) -> None:
        """Called each time the page becomes visible; refresh data here."""
        self.banner.setVisible(self.ctx.is_demo)

    def on_theme(self) -> None:
        pass

    def add_header_widget(self, w: QWidget) -> None:
        self.header_right.addWidget(w)

    def source_chip(self):
        return chip(self.ctx.provider_label)
