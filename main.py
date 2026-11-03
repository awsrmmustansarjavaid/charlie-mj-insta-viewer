"""Application entry point for Instagram Research Suite."""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from app.data.database import Database
from app.ui.main_window import MainWindow
from app.utils import configure_logging, get_data_directory


def main() -> int:
    """Configure the desktop application and start its Qt event loop."""
    data_dir = get_data_directory()
    data_dir.mkdir(parents=True, exist_ok=True)
    configure_logging(data_dir / "logs" / "application.log")

    logging.info("Starting Instagram Research Suite")
    database = Database(data_dir / "research_suite.sqlite3")
    database.initialize()

    application = QApplication(sys.argv)
    application.setApplicationName("Instagram Research Suite")
    application.setOrganizationName("InstagramResearchSuite")

    window = MainWindow(database=database, data_dir=data_dir)
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
