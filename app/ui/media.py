"""Pixmap helpers: procedural demo artwork, circular avatars, remote image cache."""

from __future__ import annotations

import hashlib
import random
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QPointF, QRectF, Qt, QUrl
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QPolygonF, QRadialGradient
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

PALETTES = [
    ("#ff9966", "#ff5e62", "#2b1055"), ("#56ccf2", "#2f80ed", "#0f2027"),
    ("#f7971e", "#ffd200", "#42275a"), ("#43cea2", "#185a9d", "#0b1b2b"),
    ("#ee9ca7", "#ffdde1", "#3a1c71"), ("#c471f5", "#fa71cd", "#1a0b2e"),
    ("#fceabb", "#f8b500", "#2c3e50"), ("#74ebd5", "#9face6", "#0f2c3d"),
]
_cache: dict[tuple, QPixmap] = {}


def art(seed: str, w: int, h: int) -> QPixmap:
    """Deterministic landscape artwork for demo media. No external assets."""
    key = ("art", seed, w, h)
    if key in _cache:
        return _cache[key]
    rng = random.Random(seed)
    top, mid, dark = rng.choice(PALETTES)
    img = QImage(w, h, QImage.Format.Format_ARGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    g = QLinearGradient(0, 0, 0, h)
    g.setColorAt(0, QColor(dark))
    g.setColorAt(0.55, QColor(mid))
    g.setColorAt(1, QColor(top))
    p.fillRect(0, 0, w, h, g)
    sx, sy = rng.uniform(0.2, 0.8) * w, rng.uniform(0.28, 0.5) * h
    rg = QRadialGradient(sx, sy, w * 0.3)
    rg.setColorAt(0, QColor(255, 255, 255, 230))
    rg.setColorAt(0.3, QColor(255, 240, 200, 120))
    rg.setColorAt(1, QColor(255, 255, 255, 0))
    p.setBrush(QBrush(rg))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(sx, sy), w * 0.3, w * 0.3)
    for layer in range(3):
        base = h * (0.55 + layer * 0.14)
        pts = [QPointF(0, h)]
        x = 0.0
        while x <= w + w / 8:
            pts.append(QPointF(x, base - rng.uniform(0.02, 0.16 - layer * 0.03) * h))
            x += w / 8
        pts.append(QPointF(w, h))
        shade = QColor(dark)
        shade.setAlpha(120 + layer * 55)
        p.setBrush(shade)
        p.drawPolygon(QPolygonF(pts))
    p.end()
    pm = QPixmap.fromImage(img)
    _cache[key] = pm
    return pm


def initials_avatar(text: str, size: int) -> QPixmap:
    """Circular avatar with a gradient derived from the name."""
    key = ("av", text, size)
    if key in _cache:
        return _cache[key]
    rng = random.Random(text)
    a, b, _ = rng.choice(PALETTES)
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    p.setClipPath(path)
    g = QLinearGradient(0, 0, size, size)
    g.setColorAt(0, QColor(a))
    g.setColorAt(1, QColor(b))
    p.fillRect(0, 0, size, size, g)
    p.setPen(QColor("white"))
    f = QFont("Segoe UI", max(7, int(size * 0.38)), QFont.Weight.Bold)
    p.setFont(f)
    p.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, (text.strip("@")[:1] or "?").upper())
    p.end()
    _cache[key] = pm
    return pm


def circle_crop(src: QPixmap, size: int) -> QPixmap:
    out = QPixmap(size, size)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    p.setClipPath(path)
    scaled = src.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation)
    p.drawPixmap((size - scaled.width()) // 2, (size - scaled.height()) // 2, scaled)
    p.end()
    return out


def ring(pix: QPixmap, size: int, seen: bool = False, accent: str = "#8B5CF6") -> QPixmap:
    """Instagram-style gradient story ring around a circular avatar."""
    pad = 5
    out = QPixmap(size + 2 * pad, size + 2 * pad)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    g = QLinearGradient(0, out.height(), out.width(), 0)
    if seen:
        g.setColorAt(0, QColor("#59637d"))
        g.setColorAt(1, QColor("#59637d"))
    else:
        for pos, col in ((0, "#feda75"), (0.35, "#fa7e1e"), (0.65, "#d62976"), (1, "#962fbf")):
            g.setColorAt(pos, QColor(col))
    p.setPen(QPen(QBrush(g), 3))
    p.drawEllipse(QRectF(1.5, 1.5, out.width() - 3, out.height() - 3))
    p.drawPixmap(pad, pad, circle_crop(pix, size))
    p.end()
    return out


class ImageCache(QObject):
    """Loads local files and HTTPS images (disk-cached) without blocking the UI."""

    def __init__(self, cache_dir: Path):
        super().__init__()
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.net = QNetworkAccessManager(self)

    def resolve(self, src: str, w: int, h: int, on_ready: Callable[[QPixmap], None] | None = None) -> QPixmap:
        """Return a pixmap now (art/placeholder), calling ``on_ready`` when a remote image arrives."""
        if not src:
            return art("empty", w, h)
        if src.startswith("seed:"):
            return art(src[5:], w, h)
        if src.startswith("https://"):
            f = self.dir / (hashlib.sha1(src.encode(), usedforsecurity=False).hexdigest() + ".img")
            if f.exists():
                pm = QPixmap(str(f))
                if not pm.isNull():
                    return pm
            if on_ready:
                reply = self.net.get(QNetworkRequest(QUrl(src)))

                def done(r=reply):
                    data = bytes(r.readAll())
                    r.deleteLater()
                    pm2 = QPixmap()
                    if pm2.loadFromData(data):
                        f.write_bytes(data)
                        on_ready(pm2)
                reply.finished.connect(done)
            return art("loading-" + src[-6:], w, h)
        pm = QPixmap(src)
        return pm if not pm.isNull() else art(src, w, h)
