"""PDF export using Qt's built-in text engine (no extra dependency)."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument

from app.services.exporter import html_document


def save_pdf(path: Path, headers: Sequence[str], rows: Sequence[Sequence[object]], title: str) -> Path:
    writer = QPdfWriter(str(path))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(12, 12, 12, 12), QPageLayout.Unit.Millimeter)
    writer.setTitle(title)
    doc = QTextDocument()
    doc.setHtml(html_document(headers, rows, title))
    doc.print_(writer)
    return path
