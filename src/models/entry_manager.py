"""
Manager for time entries storage and retrieval.
"""

import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from .time_entry import TimeEntry


class TimeEntryManager:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.entries: Dict[date, List[TimeEntry]] = {}
        self.current_entry: Optional[TimeEntry] = None
        self._load_entries()
    
    def start_timer(self, description: str = "") -> None:
        """Start a new time entry."""
        if self.current_entry is not None:
            raise RuntimeError("Timer already running")
        self.current_entry = TimeEntry(
            start_time=datetime.now(),
            end_time=datetime.now(),  # Will be updated when stopped
            description=description
        )
    
    def stop_timer(self) -> None:
        """Stop the current time entry and save it."""
        if self.current_entry is None:
            raise RuntimeError("No timer running")
        self.current_entry.end_time = datetime.now()
        self._add_entry(self.current_entry)
        self.current_entry = None
        self.save_entries()

    def resume_entry(self, entry: TimeEntry) -> None:
        """Resume an existing entry. The entry will be removed from storage and set as the current running entry.

        This prevents duplicate entries when the timer is stopped again — the entry will be re-added with an
        updated end_time.
        """
        if self.current_entry is not None:
            raise RuntimeError("Timer already running")

        entry_date = entry.date
        # Remove from existing storage so stop_timer re-adds the updated entry
        if entry_date in self.entries and entry in self.entries[entry_date]:
            self.entries[entry_date].remove(entry)
            if not self.entries[entry_date]:
                del self.entries[entry_date]

        self.current_entry = entry

    
    def add_manual_entry(self, entry: TimeEntry) -> None:
        """Add a manually created entry."""
        self._add_entry(entry)
        self.save_entries()
    
    def get_entries_for_date(self, date_: date) -> List[TimeEntry]:
        """Get all entries for a specific date."""
        return self.entries.get(date_, [])
    
    def get_total_time_for_date(self, date_: date) -> timedelta:
        """Calculate total time worked for a date (excluding absences)."""
        entries = self.get_entries_for_date(date_)
        
        # Separate work entries and absences
        work_entries = [e for e in entries if not e.is_absence]
        absence_entries = [e for e in entries if e.is_absence]
        
        # Calculate total work time
        total = timedelta()
        for work_entry in work_entries:
            work_duration = work_entry.duration
            
            # Subtract any overlapping absence time
            for absence in absence_entries:
                overlap = self._calculate_overlap(work_entry, absence)
                work_duration -= overlap
            
            total += work_duration
        
        return total
    
    def _calculate_overlap(self, entry1: TimeEntry, entry2: TimeEntry) -> timedelta:
        """Calculate the time overlap between two entries."""
        # Find the overlap period
        overlap_start = max(entry1.start_time, entry2.start_time)
        overlap_end = min(entry1.end_time, entry2.end_time)
        
        # If there's an overlap, return the duration
        if overlap_start < overlap_end:
            return overlap_end - overlap_start
        
        return timedelta()
    
    def update_entry(self, old_entry: TimeEntry, new_entry: TimeEntry) -> None:
        """Update an existing entry with new data."""
        old_date = old_entry.date
        new_date = new_entry.date
        
        # Remove from old date if dates differ
        if old_date != new_date:
            if old_date in self.entries:
                self.entries[old_date].remove(old_entry)
                if not self.entries[old_date]:
                    del self.entries[old_date]
            self._add_entry(new_entry)
        else:
            # Update in place if same date
            entries = self.entries.get(old_date, [])
            if old_entry in entries:
                idx = entries.index(old_entry)
                entries[idx] = new_entry
        
        self.save_entries()
    
    def delete_entry(self, entry: TimeEntry) -> Optional[TimeEntry]:
        """Delete an entry and remember it for undo.

        Returns the deleted entry on success or None if not found.
        """
        entry_date = entry.date
        if entry_date in self.entries:
            try:
                self.entries[entry_date].remove(entry)
                if not self.entries[entry_date]:
                    del self.entries[entry_date]
                # store last deleted for undo
                self.last_deleted = entry
                self.save_entries()
                return entry
            except ValueError:
                return None  # Entry not found
        return None

    def undo_delete(self) -> bool:
        """Restore the last deleted entry if available."""
        last = getattr(self, "last_deleted", None)
        if last is None:
            return False
        self._add_entry(last)
        self.save_entries()
        self.last_deleted = None
        return True

    def generate_report(self, start_date: date, end_date: date):
        """Generate a report data structure for a date range.

        Returns a tuple (dates, descriptions, matrix) where:
          - dates is a list of date objects from start_date to end_date (inclusive)
          - descriptions is a list of distinct descriptions (work entries + absences)
          - matrix is a dict mapping description -> list of floats (hours per day)
            Absences are shown as negative values
        """
        # Normalize dates
        if end_date < start_date:
            start_date, end_date = end_date, start_date

        num_days = (end_date - start_date).days + 1
        dates = [start_date + timedelta(days=i) for i in range(num_days)]

        # Collect entries in range
        # Map (date, description, is_absence) -> seconds
        buckets = {}
        for d in dates:
            for e in self.get_entries_for_date(d):
                # use description or label based on entry type
                if e.is_absence:
                    desc = f"🏖 Absence: {e.description.strip() if e.description else '(no description)'}"
                else:
                    desc = e.description.strip() if e.description else "(no description)"
                
                seconds = 0
                try:
                    seconds = int(e.duration.total_seconds())
                except Exception:
                    seconds = 0
                
                key = (d, desc, e.is_absence)
                buckets[key] = buckets.get(key, 0) + seconds

        # Gather unique descriptions (preserving absence flag)
        desc_keys = sorted({(desc, is_abs) for (_, desc, is_abs) in buckets.keys()})
        descriptions = [desc for desc, _ in desc_keys]

        # Build matrix mapping description -> list of hours per day
        # Absences shown as negative values
        matrix = {}
        for desc, is_absence in desc_keys:
            row = []
            for d in dates:
                secs = buckets.get((d, desc, is_absence), 0)
                hrs = round(secs / 3600.0, 2)
                # Show absences as negative values
                if is_absence:
                    hrs = -hrs
                row.append(hrs)
            matrix[desc] = row

        return dates, descriptions, matrix
    
    def _add_entry(self, entry: TimeEntry) -> None:
        """Add an entry to the entries dictionary."""
        entry_date = entry.date
        if entry_date not in self.entries:
            self.entries[entry_date] = []
        self.entries[entry_date].append(entry)
    
    def save_entries(self) -> None:
        """Save entries to storage file."""
        data = {}
        for date_, entries in self.entries.items():
            data[date_.isoformat()] = [
                entry.to_dict() for entry in entries
            ]
        self.storage_path.write_text(json.dumps(data, indent=2))
    
    def _load_entries(self) -> None:
        """Load entries from storage file."""
        if not self.storage_path.exists():
            return
        
        try:
            data = json.loads(self.storage_path.read_text())
            for date_str, entries_data in data.items():
                entry_date = date.fromisoformat(date_str)
                self.entries[entry_date] = [
                    TimeEntry.from_dict(entry_data)
                    for entry_data in entries_data
                ]
        except Exception as e:
            print(f"Error loading entries: {e}")
            self.entries = {}