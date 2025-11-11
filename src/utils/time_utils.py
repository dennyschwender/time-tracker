"""
Time-related utility functions.
"""

from datetime import datetime, timedelta
from typing import Dict, List


def calculate_weekly_hours(entries: List[Dict]) -> Dict[str, timedelta]:
    """Calculate total hours worked per week."""
    weekly_hours = {}
    
    for entry in entries:
        start = datetime.fromisoformat(entry['start_time'])
        end = datetime.fromisoformat(entry['end_time'])
        week = start.strftime('%Y-W%W')
        
        duration = end - start
        if week in weekly_hours:
            weekly_hours[week] += duration
        else:
            weekly_hours[week] = duration
    
    return weekly_hours


def format_duration(duration: timedelta) -> str:
    """Format a duration as HH:MM:SS."""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"