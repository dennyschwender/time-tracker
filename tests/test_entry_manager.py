import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime, date

# Ensure src is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models.entry_manager import TimeEntryManager
from models.time_entry import TimeEntry


def create_entry(day: date, start_h: int, duration_hours: float, desc: str = "") -> TimeEntry:
    start = datetime(day.year, day.month, day.day, start_h, 0, 0)
    end = start + timedelta(hours=duration_hours)
    return TimeEntry(start_time=start, end_time=end, description=desc)


from datetime import timedelta

def test_add_and_generate_report():
    with tempfile.TemporaryDirectory() as td:
        storage = Path(td) / "data.json"
        mgr = TimeEntryManager(storage)

        d1 = date(2025, 11, 10)
        d2 = date(2025, 11, 11)

        e1 = TimeEntry(start_time=datetime(2025,11,10,9,0,0), end_time=datetime(2025,11,10,11,0,0), description="Coding")
        e2 = TimeEntry(start_time=datetime(2025,11,10,13,0,0), end_time=datetime(2025,11,10,17,0,0), description="Meeting")
        e3 = TimeEntry(start_time=datetime(2025,11,11,9,0,0), end_time=datetime(2025,11,11,12,0,0), description="Coding")

        mgr.add_manual_entry(e1)
        mgr.add_manual_entry(e2)
        mgr.add_manual_entry(e3)

        dates, descriptions, matrix = mgr.generate_report(d1, d2)

        assert dates == [d1, d2]
        assert "Coding" in descriptions
        assert "Meeting" in descriptions
        # Check hours: Coding on d1 => 2h, d2 => 3h
        coding_row = matrix["Coding"]
        meeting_row = matrix["Meeting"]
        assert coding_row[0] == 2.0
        assert coding_row[1] == 3.0
        assert meeting_row[0] == 4.0


def test_search_entries():
    with tempfile.TemporaryDirectory() as td:
        storage = Path(td) / "data.json"
        mgr = TimeEntryManager(storage)

        d1 = date(2025, 11, 10)
        mgr.add_manual_entry(create_entry(d1, 9, 1.0, "Coding session"))
        mgr.add_manual_entry(create_entry(d1, 11, 1.0, "Team meeting"))
        mgr.add_manual_entry(create_entry(d1, 13, 1.0, "Code review"))

        results = mgr.search_entries("cod")
        descriptions = sorted(e.description for e in results)
        assert descriptions == ["Code review", "Coding session"]

        assert len(mgr.search_entries("")) == 3
        assert mgr.search_entries("nonexistent") == []


def test_get_statistics_summary():
    with tempfile.TemporaryDirectory() as td:
        storage = Path(td) / "data.json"
        mgr = TimeEntryManager(storage)

        # Mon 2025-11-10 and Tue 2025-11-11 (same week, same month)
        d1 = date(2025, 11, 10)
        d2 = date(2025, 11, 11)
        # Mon 2025-12-01 (different week and month)
        d3 = date(2025, 12, 1)

        mgr.add_manual_entry(create_entry(d1, 9, 2.0, "Coding"))
        mgr.add_manual_entry(create_entry(d2, 9, 3.0, "Coding"))
        mgr.add_manual_entry(create_entry(d3, 9, 1.0, "Coding"))

        summary = mgr.get_statistics_summary(d1, d3)

        assert len(summary["weekly"]) == 4  # weeks of Nov 10, Nov 17, Nov 24, Dec 1
        first_week = summary["weekly"][0]
        assert first_week["week_start"] == date(2025, 11, 10)
        assert first_week["total"] == timedelta(hours=5)

        last_week = summary["weekly"][-1]
        assert last_week["week_start"] == date(2025, 12, 1)
        assert last_week["total"] == timedelta(hours=1)

        assert len(summary["monthly"]) == 2
        nov = summary["monthly"][0]
        dec = summary["monthly"][1]
        assert nov == {"year": 2025, "month": 11, "total": timedelta(hours=5)}
        assert dec == {"year": 2025, "month": 12, "total": timedelta(hours=1)}


def test_save_and_load_persistence():
    with tempfile.TemporaryDirectory() as td:
        storage = Path(td) / "data.json"
        mgr = TimeEntryManager(storage)
        d = date(2025,11,12)
        e = TimeEntry(start_time=datetime(2025,11,12,8,0,0), end_time=datetime(2025,11,12,12,0,0), description="Review")
        mgr.add_manual_entry(e)
        # Recreate manager to load
        mgr2 = TimeEntryManager(storage)
        entries = mgr2.get_entries_for_date(d)
        assert len(entries) == 1
        assert entries[0].description == "Review"
