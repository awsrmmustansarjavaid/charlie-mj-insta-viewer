"""Reusable widgets: panels, metric cards, chips and painted charts."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

CHART_COLORS = ["#8B5CF6", "#22D3EE", "#F472B6", "#F59E0B", "#22C55E", "#3B82F6", "#EF4444", "#A3E635"]

STATUS_KIND = {"AVAILABLE": "ChipOk", "PARTIALLY AVAILABLE": "ChipWarn", "NOT PUBLICLY AVAILABLE": "ChipBad",
               "PERMISSION REQUIRED": "ChipWarn", "PROVIDER UNAVAILABLE": "ChipBad",
               "HISTORICAL DATA REQUIRED": "ChipWarn"}


def label(text: str = "", name: str = "", wrap: bool = False) -> QLabel:
    lb = QLabel(text)
    if name:
        lb.setObjectName(name)
    lb.setWordWrap(wrap)
    return lb


def chip(text: str, kind: str = "Chip") -> QLabel:
    lb = QLabel(text)
    lb.setObjectName(kind)
    lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lb.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return lb


def status_chip(status: str) -> QLabel:
    return chip(status, STATUS_KIND.get(status, "Chip"))


class ClickLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, e):  # noqa: N802
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)


class Panel(QFrame):
    """Rounded card with optional title; add content to ``self.body``."""

    def __init__(self, title: str = "", subtitle: str = ""):
        super().__init__()
        self.setObjectName("Panel")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(8)
        if title:
            head = QHBoxLayout()
            head.addWidget(label(title, "H2"))
            head.addStretch()
            self.head = head
            outer.addLayout(head)
        if subtitle:
            outer.addWidget(label(subtitle, "Muted", wrap=True))
        self.body = QVBoxLayout()
        self.body.setSpacing(8)
        outer.addLayout(self.body)


class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "–", delta: str = ""):
        super().__init__()
        self.setObjectName("MetricCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(2)
        lay.addWidget(label(title, "Muted"))
        self.value = label(value, "MetricValue")
        self.delta = label(delta, "Delta")
        lay.addWidget(self.value)
        lay.addWidget(self.delta)

    def set(self, value: str, delta: str = "") -> None:
        self.value.setText(value)
        self.delta.setText(delta)


def scroll_wrap(inner: QWidget) -> QScrollArea:
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    inner.setObjectName("Transparent")
    sa.setWidget(inner)
    sa.viewport().setAutoFillBackground(False)
    return sa


def make_table(headers: list[str], stretch_last: bool = True) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setShowGrid(False)
    t.setAlternatingRowColors(False)
    h = t.horizontalHeader()
    h.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    h.setStretchLastSection(stretch_last)
    h.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)  # keep source order until a header is clicked
    return t


def fill_table(t: QTableWidget, rows: list[list[object]]) -> None:
    t.setSortingEnabled(False)
    t.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            item = QTableWidgetItem()
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                item.setData(Qt.ItemDataRole.DisplayRole, v)
            else:
                item.setText("" if v is None else str(v))
            t.setItem(r, c, item)
    t.setSortingEnabled(True)


class Donut(QWidget):
    """Donut chart with legend. ``data`` maps label → value."""

    def __init__(self, center_caption: str = "Total"):
        super().__init__()
        self.data: dict[str, float] = {}
        self.caption = center_caption
        self.colors: dict[str, str] = {}
        self.setMinimumHeight(170)

    def set_data(self, data: dict[str, float], colors: dict[str, str] | None = None) -> None:
        self.data = {k: v for k, v in data.items() if v}
        self.colors = colors or {}
        self.update()

    def _color(self, i: int, k: str) -> QColor:
        return QColor(self.colors.get(k, CHART_COLORS[i % len(CHART_COLORS)]))

    def paintEvent(self, _e):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        total = sum(self.data.values())
        size = min(self.height() - 10, 170)
        rect = QRectF(8, (self.height() - size) / 2, size, size)
        fg = self.palette().text().color()
        if not total:
            p.setPen(fg)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data yet")
            return
        start = 90 * 16
        pen_w = size * 0.17
        for i, (k, v) in enumerate(self.data.items()):
            span = int(-360 * 16 * v / total)
            p.setPen(QPen(self._color(i, k), pen_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
            p.drawArc(rect.adjusted(pen_w / 2, pen_w / 2, -pen_w / 2, -pen_w / 2), start, span)
            start += span
        p.setPen(fg)
        f = QFont(self.font())
        f.setPointSize(17)
        f.setBold(True)
        p.setFont(f)
        p.drawText(rect.adjusted(0, -8, 0, -8), Qt.AlignmentFlag.AlignCenter, f"{total:,.0f}" if total > 100 else f"{total:g}")
        f.setPointSize(8)
        f.setBold(False)
        p.setFont(f)
        p.drawText(rect.adjusted(0, 26, 0, 26), Qt.AlignmentFlag.AlignCenter, self.caption)
        x, y = rect.right() + 18, 14.0
        p.setFont(self.font())
        for i, (k, v) in enumerate(self.data.items()):
            p.setBrush(self._color(i, k))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(x + 4, y + 10), 4, 4)
            p.setPen(fg)
            pct = 100 * v / total
            p.drawText(QRectF(x + 14, y, self.width() - x - 14, 20), Qt.AlignmentFlag.AlignVCenter,
                       f"{k}  {pct:.0f}%")
            y += 22


class BarChart(QWidget):
    """Horizontal bars (labels left, value right)."""

    def __init__(self, color: str = "#8B5CF6", fmt: str = "{:,.0f}"):
        super().__init__()
        self.items: list[tuple[str, float]] = []
        self.color, self.fmt = QColor(color), fmt
        self.setMinimumHeight(60)

    def set_items(self, items: list[tuple[str, float]]) -> None:
        self.items = items
        self.setMinimumHeight(max(60, 26 * len(items) + 8))
        self.update()

    def paintEvent(self, _e):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        fg = self.palette().text().color()
        if not self.items:
            p.setPen(fg)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data yet")
            return
        mx = max(v for _, v in self.items) or 1
        lw, vw = 110, 70
        for i, (k, v) in enumerate(self.items):
            y = 4 + i * 26
            p.setPen(fg)
            p.drawText(QRectF(0, y, lw, 22), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       p.fontMetrics().elidedText(str(k), Qt.TextElideMode.ElideRight, lw - 6))
            w = max(2.0, (self.width() - lw - vw) * v / mx)
            path = QPainterPath()
            path.addRoundedRect(QRectF(lw, y + 3, w, 16), 4, 4)
            p.fillPath(path, self.color)
            p.drawText(QRectF(lw + w + 6, y, vw, 22), Qt.AlignmentFlag.AlignVCenter, self.fmt.format(v))


class ColumnChart(QWidget):
    """Vertical columns, e.g. posts per hour."""

    def __init__(self, color: str = "#22D3EE"):
        super().__init__()
        self.items: list[tuple[str, float]] = []
        self.color = QColor(color)
        self.setMinimumHeight(130)

    def set_items(self, items: list[tuple[str, float]]) -> None:
        self.items = items
        self.update()

    def paintEvent(self, _e):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        fg = self.palette().text().color()
        if not self.items or not any(v for _, v in self.items):
            p.setPen(fg)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data yet")
            return
        mx = max(v for _, v in self.items)
        n = len(self.items)
        slot = self.width() / n
        for i, (k, v) in enumerate(self.items):
            h = (self.height() - 24) * v / mx
            path = QPainterPath()
            path.addRoundedRect(QRectF(i * slot + slot * 0.18, self.height() - 20 - h, slot * 0.64, h), 3, 3)
            p.fillPath(path, self.color)
            if n <= 12 or i % 3 == 0:
                p.setPen(fg)
                p.drawText(QRectF(i * slot, self.height() - 18, slot, 16), Qt.AlignmentFlag.AlignCenter, str(k))


class LineChart(QWidget):
    """Smooth-ish area/line chart."""

    def __init__(self, color: str = "#8B5CF6"):
        super().__init__()
        self.values: list[float] = []
        self.labels: list[str] = []
        self.color = QColor(color)
        self.setMinimumHeight(150)

    def set_values(self, values: list[float], labels: list[str] | None = None) -> None:
        self.values, self.labels = values, labels or []
        self.update()

    def paintEvent(self, _e):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        fg = self.palette().text().color()
        if len(self.values) < 2:
            p.setPen(fg)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Not enough data yet")
            return
        lo, hi = min(self.values), max(self.values)
        span = (hi - lo) or 1
        w, h = self.width() - 16, self.height() - 28
        pts = [QPointF(8 + i * w / (len(self.values) - 1), 6 + h - (v - lo) / span * (h - 10))
               for i, v in enumerate(self.values)]
        line = QPainterPath(pts[0])
        for a, b in zip(pts, pts[1:], strict=False):
            mid = (a.x() + b.x()) / 2
            line.cubicTo(QPointF(mid, a.y()), QPointF(mid, b.y()), b)
        area = QPainterPath(QPointF(pts[0].x(), 6 + h))
        area.lineTo(pts[0])
        area.connectPath(line)
        area.lineTo(QPointF(pts[-1].x(), 6 + h))
        area.closeSubpath()
        fill = QColor(self.color)
        fill.setAlpha(55)
        p.fillPath(area, fill)
        p.setPen(QPen(self.color, 2.4))
        p.drawPath(line)
        p.setPen(fg)
        if self.labels:
            step = max(1, len(self.labels) // 6)
            for i in range(0, len(self.labels), step):
                x0 = min(max(0, pts[i].x() - 30), self.width() - 60)
                p.drawText(QRectF(x0, self.height() - 18, 60, 16), Qt.AlignmentFlag.AlignCenter, self.labels[i])
