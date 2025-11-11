"""
Time entry dialog for manual time corrections.
"""

from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTimeEdit,
    QDateEdit,
)
from PyQt5.QtCore import Qt


class TimeEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manual Time Entry")
        self.setModal(True)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Date selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit(datetime.now())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)
        
        # Start time
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Time:"))
        self.start_time = QTimeEdit()
        self.start_time.setTime(datetime.now().time())
        start_layout.addWidget(self.start_time)
        layout.addLayout(start_layout)
        
        # End time
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End Time:"))
        self.end_time = QTimeEdit()
        self.end_time.setTime(datetime.now().time())
        end_layout.addWidget(self.end_time)
        layout.addLayout(end_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_time_entry(self):
        """Get the entered time data."""
        date = self.date_edit.date().toPyDate()
        start = datetime.combine(date, self.start_time.time().toPyTime())
        end = datetime.combine(date, self.end_time.time().toPyTime())
        
        return {
            'date': date.isoformat(),
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'duration': str(end - start)
        }