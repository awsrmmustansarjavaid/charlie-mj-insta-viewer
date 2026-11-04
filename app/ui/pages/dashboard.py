"""Overview dashboard."""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QPushButton, QWidget

from app.providers.base import ProviderError
from app.services import analytics as an
from app.ui.pages.base import Page
from app.ui.widgets import Donut, LineChart, MetricCard, Panel, fill_table, label, make_table, scroll_wrap
from app.ui.workers import run_async
from app.utils import ago_long, fmt_count


class DashboardPage(Page):
    key = "dashboard"
    title = "Dashboard"
    subtitle = "Overview of the active profile, collected data and monitoring."

    def __init__(self, ctx):
        super().__init__(ctx)
        inner = QWidget()
        grid = QGridLayout(inner)
        grid.setSpacing(12)
        self.cards = [MetricCard("Followers"), MetricCard("Following"), MetricCard("Posts"),
                      MetricCard("Avg. engagement rate")]
        for i, c in enumerate(self.cards):
            grid.addWidget(c, 0, i)
        eng = Panel("Engagement overview", "Likes on recent posts (oldest → newest)")
        self.line = LineChart()
        eng.body.addWidget(self.line)
        grid.addWidget(eng, 1, 0, 1, 2)
        types = Panel("Account type breakdown", "From the latest follower snapshot")
        self.donut = Donut("Accounts")
        types.body.addWidget(self.donut)
        grid.addWidget(types, 1, 2, 1, 2)
        act = Panel("Recent activity", "Changes are shown as 'first detected', not exact action times")
        self.events = make_table(["When detected", "Profile", "Event"])
        self.events.setMinimumHeight(220)
        act.body.addWidget(self.events)
        grid.addWidget(act, 2, 0, 1, 2)
        quick = Panel("Quick actions")
        for text, page, primary in ([
                ("View followers", "followers", False), ("View following", "followers", False),
                ("Analyse posts", "engagement", True), ("Check mentions", "mentions", True),
                ("Open Instagram view", "feed", False), ("Monitoring", "monitor", False)]):
            b = QPushButton(text)
            b.setObjectName("Primary" if primary else "")
            b.clicked.connect(lambda _=False, p=page: ctx.navigate.emit(p))
            quick.body.addWidget(b)
        self.stats = label("", "Muted", wrap=True)
        quick.body.addWidget(self.stats)
        grid.addWidget(quick, 2, 2, 1, 2)
        self.root.addWidget(scroll_wrap(inner), 1)

    def on_show(self) -> None:
        super().on_show()
        prof = self.ctx.profile
        self.add_status()

        def work():
            info = self.ctx.fetch("get_profile", prof)
            try:
                posts = self.ctx.fetch("get_posts", prof, 30)
            except ProviderError:
                posts = []
            return info, posts

        run_async(work, self._loaded, lambda e: self.stats.setText(f"Could not load profile: {e}"))
        snap = self.ctx.db.latest_snapshot(prof, "followers")
        if snap:
            self.donut.set_data(an.classify_accounts(self.ctx.db.snapshot_accounts(snap["id"])))
        else:
            self.donut.set_data({})
        ev = self.ctx.db.list_events(limit=40)
        fill_table(self.events, [[ago_long(e["detected_at"]), e["profile"], e["detail"]] for e in ev])
        s = self.ctx.db.stats()
        self.stats.setText(f"{s['profiles']} saved profiles · {s['monitors']} active monitors · "
                           f"{s['snapshots']} snapshots · {s['downloads']} downloads\nSource: {self.ctx.provider_label}")

    def add_status(self) -> None:
        pass

    def _loaded(self, result) -> None:
        info, posts = result
        self.cards[0].set(fmt_count(info.followers_count), f"@{info.username}")
        self.cards[1].set(fmt_count(info.following_count))
        self.cards[2].set(fmt_count(info.posts_count))
        rates = [r for p in posts if (r := an.engagement_rate(p, info.followers_count)) is not None]
        self.cards[3].set(f"{sum(rates) / len(rates):.2f}%" if rates else "n/a",
                          f"over {len(rates)} recent posts" if rates else "needs like counts")
        ordered = sorted(posts, key=lambda p: p.timestamp)
        self.line.set_values([float(p.likes or 0) for p in ordered],
                             [p.timestamp[5:10] for p in ordered])
