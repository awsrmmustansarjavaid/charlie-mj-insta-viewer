"""Application entry point for Instagram Research Suite."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

from PySide6.QtWidgets import QApplication

from app import __version__
from app.core.paths import configure_logging, get_data_directory
from app.data.database import Database
from app.ui.context import AppContext
from app.ui.main_window import MainWindow, app_icon


def auto_backup(db: Database, data_dir) -> None:
    """One backup per day, keeping the 10 newest."""
    folder = data_dir / "backups"
    target = folder / f"auto_{datetime.now():%Y%m%d}.sqlite3"
    if not target.exists():
        db.backup_to(target)
    for old in sorted(folder.glob("auto_*.sqlite3"))[:-10]:
        old.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Instagram Research Suite")
    parser.add_argument("--data-dir", help="Use a custom writable data directory")
    parser.add_argument("--minimized", action="store_true", help="Start hidden in the system tray")
    args, qt_args = parser.parse_known_args(argv if argv is not None else sys.argv[1:])

    data_dir = get_data_directory(args.data_dir)
    configure_logging(data_dir / "logs" / "application.log")
    logging.info("Starting Instagram Research Suite %s (data: %s)", __version__, data_dir)

    db = Database(data_dir / "database" / "research_suite.sqlite3")
    db.initialize()
    if db.integrity_check() != "ok":
        logging.error("Database integrity check failed; see Logs & diagnostics")
    if db.get_setting("auto_backup", True):
        try:
            auto_backup(db, data_dir)
        except OSError:
            logging.exception("automatic backup failed")

    app = QApplication([sys.argv[0], *qt_args])
    app.setApplicationName("Instagram Research Suite")
    app.setOrganizationName("InstagramResearchSuite")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(app_icon())
    app.setQuitOnLastWindowClosed(False)
    ctx = AppContext(db, data_dir)
    window = MainWindow(ctx, start_minimized=args.minimized)
    if not args.minimized:
        window.show()
    app.aboutToQuit.connect(lambda: logging.info("Shutting down"))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
