import pytest

from app import store


@pytest.fixture(autouse=True)
def empty_account_store(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DATABASE_PATH", tmp_path / "accounts.db")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-that-is-not-used-in-production")
    store.initialize_database()
