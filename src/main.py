#!/usr/bin/env python3
"""
Main entry point for the Time Tracking application.
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from models.settings import Settings
from gui.main_window import MainWindow
from gui.theme import apply_theme


def debug_print(msg: str) -> None:
    """Print debug messages if DEBUG mode is enabled."""
    if os.getenv('TIMETRACKER_DEBUG'):
        print(f"[DEBUG] {msg}")

def main():
    """Initialize and run the application."""
    try:
        debug_print("Starting application...")
        app = QApplication(sys.argv)
        # Load settings and apply theme early so widgets pick up stylesheet
        settings = Settings()
        theme_name = settings.get('theme', 'dark')
        apply_theme(app, theme_name)

        debug_print("Creating main window...")
        window = MainWindow(settings)
        debug_print("Showing window...")
        window.show()
        debug_print("Entering main loop...")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if os.getenv('TIMETRACKER_DEBUG'):
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    debug_print("Running main module...")
    main()