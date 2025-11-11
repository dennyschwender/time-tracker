import sys
import os
from datetime import datetime, timedelta

# Ensure src is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models.time_entry import TimeEntry


def test_duration_computation():
    start = datetime(2025, 11, 10, 9, 0, 0)
    end = datetime(2025, 11, 10, 17, 30, 0)
    entry = TimeEntry(start_time=start, end_time=end, description="Work")
    assert isinstance(entry.duration, timedelta)
    assert entry.duration == end - start
