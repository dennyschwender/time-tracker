import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from models.entry_manager import TimeEntryManager
from models.time_entry import TimeEntry


def test_resume_and_undo(tmp_path):
    storage = tmp_path / "test_data.json"
    mgr = TimeEntryManager(storage)

    # create and add an entry
    e = TimeEntry(start_time=datetime.now() - timedelta(hours=1), end_time=datetime.now(), description="Test")
    mgr.add_manual_entry(e)

    # ensure present
    date_key = e.date
    entries = mgr.get_entries_for_date(date_key)
    assert any(ent.description == "Test" for ent in entries)

    # resume the entry
    mgr.resume_entry(e)
    assert mgr.current_entry is not None

    # stop it after a moment (simulate)
    mgr.current_entry.end_time = datetime.now() + timedelta(minutes=30)
    mgr.stop_timer()

    # there should be an entry again
    entries2 = mgr.get_entries_for_date(date_key)
    assert any(ent.description == "Test" for ent in entries2)

    # delete it
    deleted = mgr.delete_entry(entries2[0])
    assert deleted is not None

    # undo delete
    ok = mgr.undo_delete()
    assert ok is True
    entries3 = mgr.get_entries_for_date(date_key)
    assert len(entries3) >= 1
