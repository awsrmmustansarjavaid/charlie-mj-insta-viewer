"""Account classification and audience overview."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QGridLayout, QHBoxLayout, QWidget

from app.providers.base import PERMISSION
from app.services import analytics as an
from app.ui.pages.base import Page
from app.ui.widgets import BarChart, Donut, MetricCard, Panel, chip, label, scroll_wrap, status_chip
from app.ui.workers import run_async

PAGES_TYPES = ("Business", "Creator", "Brand", "Media")


class InsightsPage(Page):
    key = "insights"
    title = "Account insights"
    subtitle = "Who is in your lists: account types, public vs private, verification and audience demographics."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.which = QComboBox()
        self.which.addItems(["Followers", "Following"])
        self.which.currentIndexChanged.connect(self.on_show)
        self.add_header_widget(self.which)
        inner = QWidget()
        g = QGridLayout(inner)
        g.setSpacing(12)
        self.m_total = MetricCard("Accounts in list")
        self.m_personal = MetricCard("Personal accounts")
        self.m_pages = MetricCard("Public pages / brands / creators")
        self.m_private = MetricCard("Private accounts")
        for i, m in enumerate((self.m_total, self.m_personal, self.m_pages, self.m_private)):
            g.addWidget(m, 0, i)
        p1 = Panel("Account type", "As labelled by the data source; 'Unknown' means the source gave no type")
        self.d_type = Donut("Accounts")
        p1.body.addWidget(self.d_type)
        g.addWidget(p1, 1, 0, 1, 2)
        p2 = Panel("Public vs private")
        self.d_vis = Donut("Accounts")
        p2.body.addWidget(self.d_vis)
        g.addWidget(p2, 1, 2, 1, 2)
        p3 = Panel("Verification")
        self.b_ver = BarChart("#22D3EE", "{:,.0f}")
        p3.body.addWidget(self.b_ver)
        g.addWidget(p3, 2, 0, 1, 2)
        self.aud = Panel("Audience gender")
        self.aud_status = QHBoxLayout()
        self.aud.body.addLayout(self.aud_status)
        self.d_gender = Donut("Audience %")
        self.aud_note = label("", "Muted", wrap=True)
        self.aud.body.addWidget(self.d_gender)
        self.aud.body.addWidget(self.aud_note)
        g.addWidget(self.aud, 2, 2, 1, 2)
        p4 = Panel("Age ranges (authorised insights)")
        self.b_age = BarChart("#F59E0B", "{:.0f}%")
        p4.body.addWidget(self.b_age)
        g.addWidget(p4, 3, 0, 1, 2)
        p5 = Panel("Top countries (authorised insights)")
        self.b_cty = BarChart("#3B82F6", "{:.0f}%")
        p5.body.addWidget(self.b_cty)
        g.addWidget(p5, 3, 2, 1, 2)
        why = Panel("Why there is no 'girls vs boys' count for individual accounts")
        why.body.addWidget(label(
            "Instagram does not publish a gender field for accounts, and guessing from names or photos is "
            "unreliable and intrusive. This app therefore never infers gender for individual accounts. "
            "For an account you own and have authorised, Instagram Insights reports aggregate audience gender "
            "(shown above). Everything else is shown as Unknown.", wrap=True))
        g.addWidget(why, 4, 0, 1, 4)
        self.root.addWidget(scroll_wrap(inner), 1)

    def on_show(self) -> None:
        super().on_show()
        prof = self.ctx.profile
        lt = self.which.currentText().lower()
        snap = self.ctx.db.latest_snapshot(prof, lt)
        accounts = self.ctx.db.snapshot_accounts(snap["id"]) if snap else []
        types = an.classify_accounts(accounts)
        vis = an.visibility_counts(accounts)
        n = len(accounts)
        self.m_total.set(f"{n:,}", f"snapshot #{snap['id']}" if snap else "no snapshot yet")
        personal = types.get("Personal", 0)
        pages = sum(types.get(t, 0) for t in PAGES_TYPES)
        self.m_personal.set(f"{personal:,}", f"{an.percent(personal, n)}%")
        self.m_pages.set(f"{pages:,}", f"{an.percent(pages, n)}%")
        self.m_private.set(f"{vis.get('Private', 0):,}", f"{an.percent(vis.get('Private', 0), n)}%")
        self.d_type.set_data(types)
        self.d_vis.set_data(vis, {"Public": "#22D3EE", "Private": "#8B5CF6", "Unknown": "#64748B"})
        self.b_ver.set_items(list(an.verified_counts(accounts).items()))

        def work():
            return self.ctx.fetch("get_audience", prof)

        def done(a):
            while self.aud_status.count():
                w = self.aud_status.takeAt(0).widget()
                if w:
                    w.deleteLater()
            self.aud_status.addWidget(status_chip("AVAILABLE" if a.available else PERMISSION))
            self.aud_status.addWidget(chip(a.source))
            self.aud_status.addStretch()
            self.d_gender.set_data(a.gender, {"Female": "#F472B6", "Male": "#3B82F6", "Unknown": "#64748B"})
            self.aud_note.setText(a.note)
            self.b_age.set_items(list(a.age.items()))
            self.b_cty.set_items(list(a.countries.items()))

        run_async(work, done, lambda e: (self.d_gender.set_data({}), self.aud_note.setText(str(e))))
