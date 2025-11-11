"""
Test time calculations.
"""

from datetime import datetime, timedelta
import pytest
from src.utils.time_utils import calculate_weekly_hours, format_duration


def test_calculate_weekly_hours():
    entries = [
        {
            'start_time': '2025-11-10T09:00:00',
            'end_time': '2025-11-10T17:00:00'
        },
        {
            'start_time': '2025-11-11T09:00:00',
            'end_time': '2025-11-11T17:00:00'
        }
    ]
    
    result = calculate_weekly_hours(entries)
    assert len(result) == 1
    week_key = '2025-W45'  # Week number for Nov 10, 2025
    assert week_key in result
    assert result[week_key] == timedelta(hours=16)


def test_format_duration():
    duration = timedelta(hours=2, minutes=30, seconds=15)
    result = format_duration(duration)
    assert result == "02:30:15"
    
    duration = timedelta(hours=0, minutes=45, seconds=0)
    result = format_duration(duration)
    assert result == "00:45:00"