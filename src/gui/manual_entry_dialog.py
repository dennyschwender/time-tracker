"""
Dialog for manual time entry.
"""

from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateTimeEdit,
    QLineEdit,
    QCheckBox,
)
from PyQt5.QtCore import Qt
from models.time_entry import TimeEntry


class ManualEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manual Time Entry")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Date and time inputs
        date_layout = QHBoxLayout()
        
        # Start time
        date_layout.addWidget(QLabel("Start:"))
        self.start_datetime = QDateTimeEdit(datetime.now())
        self.start_datetime.setCalendarPopup(True)
        date_layout.addWidget(self.start_datetime)
        
        # End time
        date_layout.addWidget(QLabel("End:"))
        self.end_datetime = QDateTimeEdit(datetime.now())
        self.end_datetime.setCalendarPopup(True)
        date_layout.addWidget(self.end_datetime)
        
        layout.addLayout(date_layout)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description = QLineEdit()
        layout.addWidget(self.description)
        
        # Is absence checkbox
        self.is_absence = QCheckBox("Mark as absence")
        layout.addWidget(self.is_absence)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_entry(self) -> TimeEntry:
        """Get the TimeEntry from the dialog inputs."""
        return TimeEntry(
            start_time=self.start_datetime.dateTime().toPyDateTime(),
            end_time=self.end_datetime.dateTime().toPyDateTime(),
            description=self.description.text(),
            is_absence=self.is_absence.isChecked()
        )