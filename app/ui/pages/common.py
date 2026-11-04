"""Helpers shared by several pages."""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap

from app.providers.base import Post
from app.ui.context import AppContext
from app.ui.media import circle_crop, initials_avatar, ring
from app.ui.viewers import media_pixmap


def avatar_pix(ctx: AppContext, username: str, src: str, size: int, on_ready=None) -> QPixmap:
    """Circular avatar from a profile picture, or an initials fallback."""
    if src:
        cb = (lambda pm: on_ready(circle_crop(pm, size))) if on_ready else None
        return circle_crop(ctx.pix(src, size * 2, size * 2, cb), size)
    return circle_crop(initials_avatar(username, size), size)


def story_avatar(ctx: AppContext, username: str, src: str, size: int, seen: bool, on_ready=None) -> QPixmap:
    base = ctx.pix(src, size * 2, size * 2, (lambda pm: on_ready(ring(pm, size, seen))) if on_ready else None) \
        if src else initials_avatar(username, size * 2)
    return ring(base, size, seen)


def tile_pix(ctx: AppContext, post: Post, size: int, on_ready=None) -> QPixmap:
    """Square grid tile with the Instagram-like corner glyph for reels/carousels."""
    m = post.media[0] if post.media else None
    if m is None:
        pm = QPixmap(size, size)
        pm.fill(QColor("#222"))
    else:
        src = media_pixmap(ctx, m, "IMAGE", on_ready=(lambda _p: on_ready()) if on_ready else None)
        pm = src.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation)
        x, y = (pm.width() - size) // 2, (pm.height() - size) // 2
        pm = pm.copy(x, y, size, size)
    glyph = {"REEL": "▶", "VIDEO": "▶", "CAROUSEL": "❐"}.get(post.kind, "")
    if glyph:
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor("white"))
        p.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        p.drawText(QRectF(0, 6, size - 8, 30), Qt.AlignmentFlag.AlignRight, glyph)
        p.end()
    return pm
