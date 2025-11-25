import os
import pytest
from pathlib import Path

import importlib


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Create a Flask test client and configure the app to use a temporary DB path.

    We import the application module and monkeypatch its get_db_path function so the
    tests use an isolated sqlite file under tmp_path.
    """
    # Ensure Flask app runs in testing mode
    monkeypatch.setenv("FLASK_ENV", "testing")

    # Import the app module fresh. When pytest runs with CWD=webapp, the module is named
    # "app"; when running from repo root it may be importable as "webapp.app".
    try:
        app_mod = importlib.import_module("app")
    except ModuleNotFoundError:
        app_mod = importlib.import_module("webapp.app")

    # Create a temp db path and monkeypatch get_db_path to return it
    db_file = tmp_path / "test_web_data.db"

    def _get_db_path():
        # ensure parent exists
        p = Path(db_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    monkeypatch.setattr(app_mod, "get_db_path", _get_db_path)

    # Expose the Flask test client
    flask_app = app_mod.app
    # Initialize the sqlite schema in the temporary DB
    try:
        app_mod.init_db()
    except Exception:
        # If init_db fails for any reason, tests will surface the error; ignore here
        pass
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        username = f"testuser_{tmp_path.name}"
        client.post("/api/auth/register", json={"username": username, "pin": "1234"})
        yield client
