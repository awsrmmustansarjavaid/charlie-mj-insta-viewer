"""Posts, comments, replies and emoji analytics."""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QSplitter, QVBoxLayout, QWidget

from app.providers.base import Comment, Post, ProviderError
from app.services import analytics as an
from app.ui.pages.base import Page
from app.ui.viewers import PostViewer
from app.ui.widgets import BarChart, ColumnChart, MetricCard, Panel, fill_table, label, make_table, scroll_wrap
from app.ui.workers import run_async
from app.utils import fmt_count, fmt_dt


class EngagementPage(Page):
    key = "engagement"
    title = "Posts & comments"
    subtitle = "Likes, comments, replies and emoji usage for each post, with posting patterns."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.posts: list[Post] = []
        self.followers: int | None = None
        inner = QWidget()
        lay = QVBoxLayout(inner)
        cards = QHBoxLayout()
        self.m = [MetricCard("Posts analysed"), MetricCard("Avg. likes"), MetricCard("Avg. comments"),
                  MetricCard("Avg. engagement rate")]
        for c in self.m:
            cards.addWidget(c)
        lay.addLayout(cards)

        split = QSplitter()
        left = Panel("Posts", "Double-click to open in the Instagram-style viewer")
        self.table = make_table(["Date", "Type", "Likes", "Comments", "Eng. %", "Caption"])
        self.table.setMinimumHeight(320)
        self.table.doubleClicked.connect(self._open)
        self.table.itemSelectionChanged.connect(self._select)
        left.body.addWidget(self.table)
        right = Panel("Selected post: emoji & comment analysis")
        self.sel_note = label("Select a post.", "Muted", wrap=True)
        self.groups = BarChart("#F472B6")
        self.emoji = BarChart("#8B5CF6")
        self.sent = BarChart("#22C55E")
        right.body.addWidget(self.sel_note)
        for t, w in (("Reaction-style groups (hearts, thumbs-up, …)", self.groups), ("Most-used emojis", self.emoji),
                     ("Sentiment (indicative)", self.sent)):
            right.body.addWidget(label(t, "H2"))
            right.body.addWidget(w)
        split.addWidget(left)
        split.addWidget(right)
        split.setSizes([620, 480])
        lay.addWidget(split)

        row = QHBoxLayout()
        p1 = Panel("Posts by weekday")
        self.days = ColumnChart("#22D3EE")
        p1.body.addWidget(self.days)
        p2 = Panel("Posts by hour of day")
        self.hours = ColumnChart("#8B5CF6")
        p2.body.addWidget(self.hours)
        p3 = Panel("Top hashtags")
        self.tags = BarChart("#F59E0B")
        p3.body.addWidget(self.tags)
        for p in (p1, p2, p3):
            row.addWidget(p)
        lay.addLayout(row)

        allp = Panel("All comments across recent posts",
                     "Fetches comments for up to 12 posts and totals the emoji. May take a moment on real sources.")
        self.btn_all = QPushButton("Analyse comments on all recent posts")
        self.btn_all.setObjectName("Primary")
        self.btn_all.clicked.connect(self._analyse_all)
        self.all_groups = BarChart("#F472B6")
        self.all_emoji = BarChart("#8B5CF6")
        self.all_top = BarChart("#22D3EE")
        self.all_note = label("", "Muted", wrap=True)
        allp.body.addWidget(self.btn_all)
        allp.body.addWidget(self.all_note)
        g = QGridLayout()
        g.addWidget(label("Groups", "H2"), 0, 0)
        g.addWidget(label("Top emojis", "H2"), 0, 1)
        g.addWidget(label("Top commenters", "H2"), 0, 2)
        g.addWidget(self.all_groups, 1, 0)
        g.addWidget(self.all_emoji, 1, 1)
        g.addWidget(self.all_top, 1, 2)
        allp.body.addLayout(g)
        lay.addWidget(allp)
        self.root.addWidget(scroll_wrap(inner), 1)

    def on_show(self) -> None:
        super().on_show()
        prof = self.ctx.profile

        def work():
            return self.ctx.fetch("get_profile", prof), self.ctx.fetch("get_posts", prof, 60)

        run_async(work, self._loaded, lambda e: self.sel_note.setText(f"{getattr(e, 'status', '')}: {e}"))

    def _loaded(self, res) -> None:
        info, self.posts = res
        self.followers = info.followers_count
        rates = [r for p in self.posts if (r := an.engagement_rate(p, self.followers)) is not None]
        n = len(self.posts) or 1
        likes = [p.likes for p in self.posts if p.likes is not None]
        cms = [p.comments_count for p in self.posts if p.comments_count is not None]
        self.m[0].set(str(len(self.posts)))
        self.m[1].set(fmt_count(int(sum(likes) / len(likes))) if likes else "n/a")
        self.m[2].set(fmt_count(int(sum(cms) / len(cms))) if cms else "n/a")
        self.m[3].set(f"{sum(rates) / len(rates):.2f}%" if rates else "n/a")
        fill_table(self.table, [[fmt_dt(p.timestamp)[:10], p.kind, p.likes or 0, p.comments_count or 0,
                                 an.engagement_rate(p, self.followers) or 0, p.caption[:80]] for p in self.posts])
        if self.posts:
            self.table.selectRow(0)
        d, h = an.posting_patterns(self.posts)
        self.days.set_items(list(d.items()))
        self.hours.set_items([(str(k), v) for k, v in h.items()])
        self.tags.set_items(an.hashtag_frequency(self.posts, 8))
        _ = n

    def _post_at_row(self) -> int | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        key = self.table.item(rows[0].row(), 0).text()
        cap = self.table.item(rows[0].row(), 5).text()
        for i, p in enumerate(self.posts):
            if fmt_dt(p.timestamp)[:10] == key and p.caption[:80] == cap:
                return i
        return None

    def _open(self) -> None:
        i = self._post_at_row()
        if i is not None:
            PostViewer(self.ctx, self.posts, i, self, self.followers).exec()

    def _select(self) -> None:
        i = self._post_at_row()
        if i is None:
            return
        post = self.posts[i]
        self.sel_note.setText("Loading comments…")

        def work():
            return self.ctx.registry.call("get_comments", post, fallback=False)

        def done(comments: list[Comment]):
            counts = an.emoji_counts(comments)
            self.sel_note.setText(f"{len(an.flatten_comments(comments))} comments and replies retrieved. Counts are "
                                  "emoji found in comment text, not Instagram like-button reactions.")
            self.groups.set_items(list(an.emoji_group_counts(counts).items()))
            self.emoji.set_items(list(counts.items())[:10])
            self.sent.set_items(list(an.sentiment(comments).items()))

        run_async(work, done, lambda e: self.sel_note.setText(f"{getattr(e, 'status', '')}: {e}"))

    def _analyse_all(self) -> None:
        posts = self.posts[:12]
        self.btn_all.setEnabled(False)

        def work(progress):
            allc: list[Comment] = []
            for i, p in enumerate(posts):
                try:
                    allc += self.ctx.registry.call("get_comments", p, fallback=False)
                except ProviderError:
                    pass
                progress(i + 1, len(posts))
            return allc

        def done(allc):
            self.btn_all.setEnabled(True)
            counts = an.emoji_counts(allc)
            self.all_note.setText(f"{len(an.flatten_comments(allc))} comments/replies from {len(posts)} posts.")
            self.all_groups.set_items(list(an.emoji_group_counts(counts).items()))
            self.all_emoji.set_items(list(counts.items())[:10])
            self.all_top.set_items(an.top_commenters(allc, 8))

        run_async(work, done, lambda e: (self.btn_all.setEnabled(True), self.all_note.setText(str(e))),
                  on_progress=lambda n, t: self.all_note.setText(f"Fetching comments… {n}/{t}"))
