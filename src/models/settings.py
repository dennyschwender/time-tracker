"""
Application settings model.
"""

import json
from pathlib import Path
from typing import Dict, Any


class Settings:
    """Manages application settings."""
    
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or Path.home() / '.timetracking' / 'config.json'
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load settings from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._default_settings()
            self.save()
    
    def save(self):
        """Save settings to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _default_settings(self) -> Dict[str, Any]:
        """Return default settings."""
        return {
            'work_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'work_hours': {
                'start': '09:00',
                'end': '17:00'
            },
            'break_duration': 60,  # minutes
            'data_directory': str(Path.home() / '.timetracking' / 'data'),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value."""
        self.config[key] = value
        self.save()