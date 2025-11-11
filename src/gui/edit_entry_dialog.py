"""
Dialog for editing existing time entries.
"""

from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateTimeEdit,
    QLineEdit,
    QCheckBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from models.time_entry import TimeEntry


class EditEntryDialog(QDialog):
    def __init__(self, entry: TimeEntry, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Time Entry")
        self.setModal(True)
        self.entry = entry
        
        layout = QVBoxLayout(self)
        
        # Date and time inputs
        date_layout = QHBoxLayout()
        
        # Start time
        date_layout.addWidget(QLabel("Start:"))
        self.start_datetime = QDateTimeEdit(entry.start_time)
        self.start_datetime.setCalendarPopup(True)
        date_layout.addWidget(self.start_datetime)
        
        # End time
        date_layout.addWidget(QLabel("End:"))
        self.end_datetime = QDateTimeEdit(entry.end_time)
        self.end_datetime.setCalendarPopup(True)
        date_layout.addWidget(self.end_datetime)
        
        layout.addLayout(date_layout)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description = QLineEdit(entry.description)
        layout.addWidget(self.description)
        
        # Is absence checkbox
        self.is_absence = QCheckBox("Mark as absence")
        self.is_absence.setChecked(entry.is_absence)
        layout.addWidget(self.is_absence)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._on_delete)
        delete_button.setStyleSheet("background-color: #ffcccc;")
        button_layout.addWidget(delete_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Store the deletion flag
        self.should_delete = False
    
    def _on_delete(self):
        """Handle delete button click."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this entry?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.should_delete = True
            self.accept()
    
    def get_updated_entry(self) -> TimeEntry:
        """Get an updated TimeEntry from the dialog inputs."""
        return TimeEntry(
            start_time=self.start_datetime.dateTime().toPyDateTime(),
            end_time=self.end_datetime.dateTime().toPyDateTime(),
            description=self.description.text(),
            is_absence=self.is_absence.isChecked()
        )