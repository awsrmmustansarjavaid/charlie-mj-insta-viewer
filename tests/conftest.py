import pytest

from app.data.database import Database
from app.providers.registry import ProviderRegistry


@pytest.fixture()
def db(tmp_path):
    d = Database(tmp_path / "t.sqlite3")
    d.initialize()
    return d


@pytest.fixture()
def registry(db):
    return ProviderRegistry(db)
