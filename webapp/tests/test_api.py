import os
import json


def test_ping(client):
    resp = client.get("/api/ping")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("ok") is True


def test_save_load_entries_disabled(client):
    # When server persistence is disabled, API should return 403
    # Ensure env var is not set
    if "USE_SERVER_DB" in os.environ:
        del os.environ["USE_SERVER_DB"]
    r = client.post("/api/save_entries", json={"entries": []})
    assert r.status_code == 403


def test_save_and_load_entries_enabled(client, monkeypatch):
    # Enable server persistence and exercise save/load
    monkeypatch.setenv("USE_SERVER_DB", "1")
    # Save two entries
    entries = [
        {"date": "2025-11-11", "start": "09:00", "end": "10:00", "description": "Work", "is_absence": False},
        {"date": "2025-11-11", "start": "10:30", "end": "11:00", "description": "Meeting", "is_absence": False},
    ]
    r = client.post("/api/save_entries", json={"entries": entries})
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("saved") == 2

    # Load entries back
    r2 = client.get("/api/load_entries")
    assert r2.status_code == 200
    d2 = r2.get_json()
    loaded = d2.get("entries")
    # Expect two entries and matching descriptions
    assert isinstance(loaded, list)
    assert len(loaded) == 2
    descs = {e["description"] for e in loaded}
    assert descs == {"Work", "Meeting"}
