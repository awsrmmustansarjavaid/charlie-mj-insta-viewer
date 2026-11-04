"""Theme engine: dark/light, accent colour, card style, density, wallpaper."""

from __future__ import annotations

from dataclasses import asdict, dataclass

ACCENTS = {"Purple": "#8B5CF6", "Cyan": "#22D3EE", "Blue": "#3B82F6", "Green": "#22C55E",
           "Pink": "#EC4899", "Orange": "#F59E0B"}


@dataclass
class Theme:
    mode: str = "Dark"            # Dark | Light
    accent: str = "Purple"
    card_style: str = "Glass"     # Solid | Glass | Minimal
    density: str = "Comfortable"  # Comfortable | Compact
    background: str = "Gradient"  # Gradient | Solid | Image
    background_image: str = ""
    background_dim: int = 55      # % darkening over custom image
    animations: bool = True
    sidebar_compact: bool = False

    @classmethod
    def from_dict(cls, d: dict | None) -> Theme:
        t = cls()
        for k, v in (d or {}).items():
            if hasattr(t, k):
                setattr(t, k, v)
        return t

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def accent_hex(self) -> str:
        return ACCENTS.get(self.accent, ACCENTS["Purple"])

    @property
    def dark(self) -> bool:
        return self.mode != "Light"

    def palette(self) -> dict[str, str]:
        if self.dark:
            return dict(bg="#0B1020", sidebar="#0D1425", card="#11182A", card_alt="#17243B",
                        border="#263653", text="#E7ECF7", muted="#93A4C2", input="#0D172B",
                        hover="#2C3C60", btn="#202D49", btn_border="#344565", ok="#22C55E",
                        warn="#F59E0B", bad="#EF4444", cyan="#22D3EE")
        return dict(bg="#F3F5FB", sidebar="#FFFFFF", card="#FFFFFF", card_alt="#EEF1F8",
                    border="#D5DBEA", text="#161B2E", muted="#5C6785", input="#FFFFFF",
                    hover="#E3E8F5", btn="#EEF1F8", btn_border="#CBD3E6", ok="#16A34A",
                    warn="#D97706", bad="#DC2626", cyan="#0891B2")

    def panel_background(self) -> str:
        p = self.palette()
        if self.card_style == "Glass":
            return "rgba(17,26,46,175)" if self.dark else "rgba(255,255,255,200)"
        if self.card_style == "Minimal":
            return "transparent"
        return p["card"]


def build_stylesheet(t: Theme) -> str:
    p, a = t.palette(), t.accent_hex
    pad = "6px" if t.density == "Compact" else "9px"
    panel_bg = t.panel_background()
    panel_border = "none" if t.card_style == "Minimal" else f"1px solid {p['border']}"
    return f"""
QMainWindow, QDialog {{ background: {p['bg']}; }}
QWidget {{ color: {p['text']}; font-family: "Segoe UI", "Inter", "Arial"; font-size: 10pt; }}
QLabel, QCheckBox, QRadioButton, QStackedWidget, QScrollArea, QTabWidget::pane {{ background: transparent; }}
QWidget#Transparent, QWidget#Page {{ background: transparent; }}
QWidget#Sidebar {{ background: {p['sidebar']}; border-right: 1px solid {p['border']}; }}
QLabel#Brand {{ font-size: 13pt; font-weight: 700; }}
QLabel#Muted {{ color: {p['muted']}; }}
QLabel#Section {{ color: {p['muted']}; font-size: 8pt; font-weight: 700; letter-spacing: 1px;
                 padding: 10px 6px 2px 6px; }}
QLabel#PageTitle {{ font-size: 19pt; font-weight: 700; }}
QLabel#H2 {{ font-size: 12pt; font-weight: 600; }}
QLabel#MetricValue {{ font-size: 21pt; font-weight: 700; }}
QLabel#Delta {{ color: {p['ok']}; font-size: 9pt; }}
QLabel#Chip {{ background: {p['card_alt']}; border: 1px solid {p['border']}; border-radius: 9px;
               padding: 2px 9px; font-size: 8pt; font-weight: 600; }}
QLabel#ChipOk {{ background: rgba(34,197,94,40); color: {p['ok']}; border-radius: 9px; padding: 2px 9px;
                font-size: 8pt; font-weight: 600; }}
QLabel#ChipWarn {{ background: rgba(245,158,11,45); color: {p['warn']}; border-radius: 9px; padding: 2px 9px;
                  font-size: 8pt; font-weight: 600; }}
QLabel#ChipBad {{ background: rgba(239,68,68,40); color: {p['bad']}; border-radius: 9px; padding: 2px 9px;
                 font-size: 8pt; font-weight: 600; }}
QFrame#Panel, QFrame#MetricCard {{ background: {panel_bg}; border: {panel_border}; border-radius: 14px; }}
QFrame#PostCard {{ background: {panel_bg}; border: {panel_border}; border-radius: 10px; }}
QFrame#Banner {{ background: rgba(245,158,11,30); border: 1px solid {p['warn']}; border-radius: 10px; }}
QPushButton {{ background: {p['btn']}; color: {p['text']}; border: 1px solid {p['btn_border']};
               border-radius: 8px; padding: {pad} 13px; }}
QPushButton:hover {{ background: {p['hover']}; border-color: {a}; }}
QPushButton:disabled {{ color: {p['muted']}; }}
QPushButton#Primary {{ background: {a}; color: white; border: 1px solid {a}; font-weight: 600; }}
QPushButton#Primary:hover {{ background: {a}; border-color: white; }}
QPushButton#Flat {{ background: transparent; border: none; padding: 4px 8px; }}
QPushButton#Flat:hover {{ color: {a}; }}
QPushButton#Nav {{ text-align: left; padding: {pad} 12px; background: transparent; border: none;
                  border-radius: 8px; color: {p['muted']}; }}
QPushButton#Nav:hover {{ background: {p['card_alt']}; color: {p['text']}; }}
QPushButton#Nav:checked {{ background: {a}; color: white; font-weight: 600; }}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit, QTextBrowser {{
    background: {p['input']}; color: {p['text']}; border: 1px solid {p['border']}; border-radius: 8px;
    padding: 6px; selection-background-color: {a}; }}
QLineEdit:focus, QComboBox:focus {{ border-color: {a}; }}
QComboBox QAbstractItemView {{ background: {p['card']}; color: {p['text']}; selection-background-color: {a}; }}
QTableView, QTableWidget, QListWidget, QTreeWidget {{
    background: {panel_bg if t.card_style != 'Minimal' else p['input']}; alternate-background-color: transparent;
    border: 1px solid {p['border']}; border-radius: 10px; gridline-color: {p['border']};
    selection-background-color: {a}; selection-color: white; }}
QHeaderView::section {{ background: {p['card_alt']}; color: {p['muted']}; border: none; padding: 7px;
                       font-weight: 600; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ background: transparent; color: {p['muted']}; padding: 8px 15px; border-bottom: 2px solid transparent; }}
QTabBar::tab:selected {{ color: {p['text']}; border-bottom: 2px solid {a}; font-weight: 600; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: {p['btn_border']}; border-radius: 5px; min-height: 30px; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; }}
QScrollBar::handle:horizontal {{ background: {p['btn_border']}; border-radius: 5px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QProgressBar {{ background: {p['card_alt']}; border: none; border-radius: 4px; height: 8px; text-align: center; }}
QProgressBar::chunk {{ background: {a}; border-radius: 4px; }}
QToolTip {{ background: {p['card']}; color: {p['text']}; border: 1px solid {a}; padding: 4px; }}
QMenu {{ background: {p['card']}; border: 1px solid {p['border']}; }}
QMenu::item:selected {{ background: {a}; color: white; }}
"""
