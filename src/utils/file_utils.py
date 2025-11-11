"""
File operation utilities.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def load_time_entries(data_dir: Path) -> List[Dict]:
    """Load time entries from JSON files."""
    entries = []
    data_dir.mkdir(parents=True, exist_ok=True)
    
    for file in data_dir.glob('*.json'):
        try:
            with open(file, 'r') as f:
                entries.extend(json.load(f))
        except (json.JSONDecodeError, IOError):
            continue
    
    return entries


def save_time_entry(entry: Dict, data_dir: Path):
    """Save a time entry to a JSON file."""
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use YYYY-MM.json as filename format
    date = datetime.fromisoformat(entry['date'])
    filename = date.strftime('%Y-%m.json')
    file_path = data_dir / filename
    
    # Load existing entries
    entries = []
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                entries = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Add new entry and save
    entries.append(entry)
    with open(file_path, 'w') as f:
        json.dump(entries, f, indent=2)