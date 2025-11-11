"""
Timer widget implementation for the Time Tracking application.
"""

from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
)
from PyQt5.QtCore import QTimer, Qt


class TimerWidget(QWidget):
    def __init__(self, entry_manager):
        super().__init__()
        self.entry_manager = entry_manager
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_display)
        self.timer.setInterval(1000)  # Update every second
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Time display
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.time_label)
        
        # Description input (below clock)
        self.description = QLineEdit()
        self.description.setPlaceholderText("Work description...")
        layout.addWidget(self.description)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_timer)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
    
    def start_timer(self):
        """Start the timer."""
        try:
            self.entry_manager.start_timer(self.description.text())
            self.timer.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.description.setEnabled(False)
        except RuntimeError as e:
            QMessageBox.warning(self, "Error", str(e))

    def resume_current(self):
        """Resume the currently set entry in the manager (do not create a new one)."""
        if self.entry_manager.current_entry is None:
            QMessageBox.warning(self, "Error", "No entry to resume")
            return
        # Populate UI from current entry
        entry = self.entry_manager.current_entry
        try:
            # If entry has a description, show it
            self.description.setText(entry.description or "")
            self.description.setEnabled(False)
        except Exception:
            pass

        # Start timer UI
        self.timer.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self._update_display()
    
    def stop_timer(self):
        """Stop the timer."""
        try:
            self.entry_manager.stop_timer()
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.description.clear()
            self.description.setEnabled(True)
            self._update_display()
        except RuntimeError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def _update_display(self):
        """Update the time display."""
        if self.entry_manager.current_entry:
            duration = datetime.now() - self.entry_manager.current_entry.start_time
        else:
            duration = timedelta()
        
        # Format as HH:MM:SS
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")