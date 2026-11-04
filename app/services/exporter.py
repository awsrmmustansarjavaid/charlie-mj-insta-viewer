"""Export rows to CSV, Excel, JSON, HTML and Markdown. (PDF lives in the UI layer
because it uses Qt's text-to-PDF engine.)"""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Sequence

Rows = Sequence[Sequence[object]]


def to_csv(path: Path, headers: Sequence[str], rows: Rows) -> Path:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:  # BOM: opens cleanly in Excel
        w = csv.writer(fh)
        w.writerow(headers)
        w.writerows(rows)
    return path


def to_xlsx(path: Path, headers: Sequence[str], rows: Rows, title: str = "Data") -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]
    ws.append(list(headers))
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="713CEB")
    for r in rows:
        ws.append(["" if v is None else v for v in r])
    for i, h in enumerate(headers, 1):
        width = max([len(str(h))] + [len(str(r[i - 1])) for r in rows[:300]]) + 2
        ws.column_dimensions[ws.cell(1, i).column_letter].width = min(width, 50)
    ws.freeze_panes = "A2"
    wb.save(path)
    return path


def to_json(path: Path, headers: Sequence[str], rows: Rows) -> Path:
    path.write_text(json.dumps([dict(zip(headers, r, strict=False)) for r in rows], indent=2, ensure_ascii=False),
                    encoding="utf-8")
    return path


def to_markdown(path: Path, headers: Sequence[str], rows: Rows, title: str = "Report") -> Path:
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(str(v).replace("|", "\\|") for v in r) + " |" for r in rows]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def html_document(headers: Sequence[str], rows: Rows, title: str = "Report") -> str:
    head = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in r) + "</tr>" for r in rows)
    return (f"<html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>"
            "body{font-family:Segoe UI,Arial;margin:24px}table{border-collapse:collapse;width:100%}"
            "th{background:#713CEB;color:#fff;text-align:left}td,th{padding:6px 10px;border-bottom:1px solid #ddd;"
            "font-size:12px}</style></head><body>"
            f"<h2>{html.escape(title)}</h2><table><tr>{head}</tr>{body}</table></body></html>")


def to_html(path: Path, headers: Sequence[str], rows: Rows, title: str = "Report") -> Path:
    path.write_text(html_document(headers, rows, title), encoding="utf-8")
    return path


FORMATS = {"CSV": ".csv", "Excel": ".xlsx", "JSON": ".json", "HTML": ".html", "Markdown": ".md", "PDF": ".pdf"}
