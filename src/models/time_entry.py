"""
Time entry data model.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Optional


@dataclass
class TimeEntry:
    """Represents a single time entry."""
    start_time: datetime
    end_time: datetime
    description: str = ""
    is_absence: bool = False
    
    @property
    def date(self) -> date:
        """Get the date of this entry."""
        return self.start_time.date()
    
    @property
    def duration(self) -> timedelta:
        """Calculate the duration of this entry."""
        return self.end_time - self.start_time
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TimeEntry':
        """Create a TimeEntry from a dictionary."""
        return cls(
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            description=data.get('description', ''),
            is_absence=data.get('is_absence', False)
        )
    
    def to_dict(self) -> dict:
        """Convert the TimeEntry to a dictionary."""
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'description': self.description,
            'is_absence': self.is_absence
        }