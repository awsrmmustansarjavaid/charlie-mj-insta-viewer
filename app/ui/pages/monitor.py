"""Monitoring dashboard: scheduled checks for multiple profiles."""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QSpinBox

from app.ui.pages.base import Page
from app.ui.widgets import fill_table, label, make_table
from app.utils import fmt_dt, parse_username


class MonitorPage(Page):
    key = "monitor"
    title = "Monitoring"
    subtitle = ("Automatic checks for new posts, reels, stories, mentions, profile changes and list changes. "
                "Runs in the background while the app is open (or minimised to the tray).")

    def __init__(self, ctx, scheduler):
        super().__init__(ctx)
        self.sched = scheduler
        top = QHBoxLayout()
        self.enabled = QCheckBox("Background monitoring on")
        self.enabled.setChecked(scheduler.enabled)
        self.enabled.toggled.connect(scheduler.set_enabled)
        self.state = label("", "Muted")
        top.addWidget(self.enabled)
        top.addWidget(self.state, 1)
        self.sim = QPushButton("⏩ Simulate time passing (demo)")
        self.sim.clicked.connect(self._simulate)
        top.addWidget(self.sim)
        self.root.addLayout(top)

        add = QHBoxLayout()
        self.user = QLineEdit()
        self.user.setPlaceholderText("Username to monitor")
        self.interval = QComboBox()
        for label_, mins in (("every 15 min", 15), ("every 30 min", 30), ("hourly", 60), ("every 6 hours", 360),
                             ("daily", 1440), ("weekly", 10080)):
            self.interval.addItem(label_, mins)
        self.interval.setCurrentIndex(2)
        self.priority = QSpinBox()
        self.priority.setRange(1, 9)
        self.priority.setValue(5)
        self.priority.setPrefix("priority ")
        btn = QPushButton("Add monitor")
        btn.setObjectName("Primary")
        btn.clicked.connect(self._add)
        for w in (self.user, self.interval, self.priority, btn):
            add.addWidget(w, 1 if w is self.user else 0)
        self.root.addLayout(add)

        self.table = make_table(["Profile", "Enabled", "Interval (min)", "Priority", "Last run", "Next run",
                                 "Status", "Errors"])
        self.root.addWidget(self.table, 1)
        acts = QHBoxLayout()
        for text, fn in (("▶ Run now", self._run), ("⏯ Pause / resume", self._toggle), ("🗑 Remove", self._remove)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            acts.addWidget(b)
        acts.addStretch()
        self.root.addLayout(acts)
        self.root.addWidget(label(
            "Rules: a profile is never scanned twice at once · the first check records a silent baseline · after 5 "
            "consecutive failures a monitor pauses itself and notifies you · changes are reported as 'first detected'.",
            "Muted", wrap=True))
        scheduler.state_changed.connect(self._state)
        ctx.data_changed.connect(self._fill)

    def on_show(self) -> None:
        super().on_show()
        self.sim.setVisible(self.ctx.is_demo)
        self._fill()
        self._state()

    def _state(self) -> None:
        self.state.setText(f"Running a check for @{self.sched.running}…" if self.sched.running else
                           ("Idle · next check within 30 seconds of the schedule" if self.sched.enabled
                            else "Paused"))
        self._fill()

    def _fill(self) -> None:
        fill_table(self.table, [[m["profile"], "yes" if m["enabled"] else "paused", m["interval_minutes"],
                                 m["priority"], fmt_dt(m["last_run"] or ""), fmt_dt(m["next_run"] or ""),
                                 m["last_status"], m["consecutive_errors"]] for m in self.ctx.db.list_monitors()])

    def _sel(self) -> str | None:
        r = self.table.selectionModel().selectedRows()
        return self.table.item(r[0].row(), 0).text() if r else None

    def _add(self) -> None:
        u = parse_username(self.user.text())
        if u:
            self.ctx.db.upsert_monitor(u, self.interval.currentData(), True, self.priority.value())
            self.user.clear()
            self._fill()

    def _run(self) -> None:
        if u := self._sel():
            self.sched.run(u)

    def _toggle(self) -> None:
        if u := self._sel():
            row = next(m for m in self.ctx.db.list_monitors() if m["profile"] == u)
            self.ctx.db.upsert_monitor(u, row["interval_minutes"], not row["enabled"], row["priority"])
            self._fill()

    def _remove(self) -> None:
        if (u := self._sel()) and QMessageBox.question(self, "Remove", f"Stop monitoring @{u}?") == \
                QMessageBox.StandardButton.Yes:
            self.ctx.db.delete_monitor(u)
            self._fill()

    def _simulate(self) -> None:
        n = int(self.ctx.db.get_setting("demo_epoch", 0)) + 1
        self.ctx.db.save_setting("demo_epoch", n)
        self.ctx.invalidate()
        self.ctx.toast.emit("Demo time advanced", f"Step {n}: new followers, unfollows and posts will be "
                            "detected at the next check. Click 'Run now' on a monitor.")
