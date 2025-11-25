"""Helper to interact with the Flask webapp's persistence API."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from models.time_entry import TimeEntry

REMOTE_TIME_FORMATS = ["%H:%M:%S", "%H:%M"]


def _combine_date_and_time(date_str: str, time_str: str) -> datetime:
    if not date_str or not time_str:
        raise ValueError("Remote entry missing date/time information")

    try:
        return datetime.fromisoformat(time_str)
    except ValueError:
        pass

    for fmt in REMOTE_TIME_FORMATS:
        try:
            parsed = datetime.strptime(time_str, fmt)
            parsed_date = date.fromisoformat(date_str)
            return datetime(
                parsed_date.year,
                parsed_date.month,
                parsed_date.day,
                parsed.hour,
                parsed.minute,
                parsed.second,
            )
        except ValueError:
            continue

    raise ValueError(f"Unable to parse remote time '{time_str}'")


def _entry_to_payload(entry: TimeEntry) -> Dict[str, Any]:
    return {
        "date": entry.start_time.date().isoformat(),
        "start": entry.start_time.strftime("%H:%M:%S"),
        "end": entry.end_time.strftime("%H:%M:%S"),
        "description": entry.description,
        "is_absence": entry.is_absence,
    }


def _entry_from_payload(payload: Dict[str, Any]) -> TimeEntry:
    entry_date = payload.get("date")
    if not entry_date:
        raise ValueError("Missing date for remote entry")

    start_time = _combine_date_and_time(entry_date, payload.get("start", ""))
    end_time = _combine_date_and_time(entry_date, payload.get("end", ""))

    return TimeEntry(
        start_time=start_time,
        end_time=end_time,
        description=payload.get("description", ""),
        is_absence=bool(payload.get("is_absence")),
    )


class RemoteTimeTrackerClient:
    """Minimal client for the Flask API that stores time entries."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def login(self, username: str, pin: str) -> None:
        resp = self.session.post(
            self._url("/api/auth/login"),
            json={"username": username, "pin": pin},
        )
        resp.raise_for_status()

    def load_entries(self) -> List[TimeEntry]:
        resp = self.session.get(self._url("/api/load_entries"))
        resp.raise_for_status()
        data = resp.json() or {}
        entries = data.get("entries", [])
        return [_entry_from_payload(item) for item in entries]

    def save_entries(self, entries: List[TimeEntry]) -> Dict[str, Any]:
        payload = {"entries": [_entry_to_payload(entry) for entry in entries]}
        resp = self.session.post(self._url("/api/save_entries"), json=payload)
        resp.raise_for_status()
        return resp.json()


def remote_entries_from_payload(entries: List[Dict[str, Any]]) -> List[TimeEntry]:
    return [_entry_from_payload(entry) for entry in entries]


def remote_entry_payload(entry: TimeEntry) -> Dict[str, Any]:
    return _entry_to_payload(entry)
