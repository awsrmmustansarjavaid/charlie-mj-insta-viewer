"""Backward-compatible import path for the SQLite database implementation.

The maintained implementation lives in :mod:`app.data.database`; this module
keeps older tests and downstream imports working during the package transition.
"""

from app.data.database import Database

__all__ = ["Database"]
