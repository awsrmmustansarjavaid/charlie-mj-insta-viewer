"""Application entry point and Qt startup configuration."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from instagram_research_suite.storage.database import Database
from instagram_research_suite.ui.main_window import MainWindow


def main() -> int:
    """Create the Qt application, initialise local storage, and show the main window."""
    app = QApplication(sys.argv)
    app.setApplicationName("Instagram Research Suite")
    app.setOrganizationName("InstagramResearchSuite")

    # Initialise the local database before the UI starts requesting snapshots.
    database = Database()
    database.initialize()

    window = MainWindow(database=database)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
