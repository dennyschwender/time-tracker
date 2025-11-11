"""
Main window implementation for the Time Tracking application.
"""

from pathlib import Path
from datetime import date
from appdirs import user_data_dir
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QCalendarWidget,
    QLabel,
    QMenu,
    QAction,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, QDate
from models.entry_manager import TimeEntryManager
from .timer_widget import TimerWidget
from .manual_entry_dialog import ManualEntryDialog
from .edit_entry_dialog import EditEntryDialog
from .report_dialog import ReportDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracking")
        self.resize(800, 600)
        
        # Initialize entry manager using platform-standard user data dir
        appname = "TimeTracker"
        appauthor = "dennyschwender"
        data_dir = Path(user_data_dir(appname, appauthor))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.entry_manager = TimeEntryManager(data_dir / "timedata.json")

        # Set up the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        # Create timer widget
        self.timer_widget = TimerWidget(self.entry_manager)
        layout.addWidget(self.timer_widget)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self._on_date_selected)
        layout.addWidget(self.calendar)
        
        # Daily summary
        self.entries_list = QListWidget()
        self.entries_list.itemDoubleClicked.connect(self._on_entry_double_clicked)
        self.entries_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.entries_list.customContextMenuRequested.connect(self._show_entry_context_menu)
        self.entries_list.setSpacing(2)
        self.entries_list.setWordWrap(True)
        self.entries_list.setAlternatingRowColors(True)
        layout.addWidget(self.entries_list)
        
        # Update summary for today
        self._on_date_selected(date.today())
        
        # Set up menus
        self._create_menus()
    
    def _create_menus(self):
        """Create the application menus."""
        menubar = self.menuBar()
        assert menubar is not None
        
        # File menu
        file_menu = QMenu("&File", self)
        menubar.addMenu(file_menu)
        
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self._on_exit)
        file_menu.addAction(exit_action)
        
        # Export report
        export_action = QAction("Export Report...", self)
        export_action.setStatusTip("Export time report to Excel")
        export_action.triggered.connect(self._show_export_report)
        file_menu.addAction(export_action)
        
        # Tools menu
        tools_menu = QMenu("&Tools", self)
        menubar.addMenu(tools_menu)
        
        manual_entry = QAction("&Manual Entry", self)
        manual_entry.setStatusTip("Manually enter time")
        manual_entry.triggered.connect(self._show_manual_entry)
        tools_menu.addAction(manual_entry)

    
    
    def _on_date_selected(self, selected_date):
        """Update summary when a date is selected."""
        if isinstance(selected_date, QDate):
            selected_date = selected_date.toPyDate()
            
        entries = self.entry_manager.get_entries_for_date(selected_date)
        total_time = self.entry_manager.get_total_time_for_date(selected_date)
        
        # Clear and repopulate entries list
        self.entries_list.clear()
        
        # Add header item
        hours = total_time.total_seconds() / 3600
        absences = sum(1 for e in entries if e.is_absence)
        
        date_str = selected_date.strftime("%A, %d %B %Y")
        header = QListWidgetItem(
            f"{date_str}\n"
            f"Total Hours Worked: {hours:.2f}h | "
            f"Entries: {len(entries)} | "
            f"Absences: {absences}"
        )
        header.setFlags(Qt.ItemFlag(header.flags() & ~Qt.ItemFlag.ItemIsEnabled))
        header.setBackground(self.entries_list.palette().alternateBase())
        font = header.font()
        font.setBold(True)
        header.setFont(font)
        self.entries_list.addItem(header)
        
        # Add spacer after header
        self.entries_list.addItem("")
        
        # Sort entries by start time
        sorted_entries = sorted(entries, key=lambda e: e.start_time)
        
        # Add entries
        for entry in sorted_entries:
            if entry.is_absence:
                text = f"🏖  Absence - {entry.description}"
                item = QListWidgetItem(text)
                item.setForeground(Qt.GlobalColor.darkRed)
            else:
                start = entry.start_time.strftime("%H:%M")
                end = entry.end_time.strftime("%H:%M")
                duration = entry.duration.total_seconds() / 3600
                text = f"⏰ {start} - {end}  ({duration:.2f}h)"
                if entry.description:
                    text += f"\n   📝 {entry.description}"
                item = QListWidgetItem(text)
                item.setForeground(Qt.GlobalColor.darkBlue)
            
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.entries_list.addItem(item)
            
            # Add small spacer between entries
            if entry != sorted_entries[-1]:
                self.entries_list.addItem("")
    
    def _on_entry_double_clicked(self, item):
        """Handle double-click on an entry."""
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry:
            self._edit_entry(entry)
    
    def _show_entry_context_menu(self, pos):
        """Show context menu for entries."""
        item = self.entries_list.itemAt(pos)
        if not item:
            return
        
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        
        menu = QMenu(self)
        # Resume only for non-absence entries
        resume_action = None
        if not getattr(entry, 'is_absence', False):
            resume_action = menu.addAction("Resume")
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(self.entries_list.mapToGlobal(pos))
        
        if action == edit_action:
            self._edit_entry(entry)
        elif resume_action is not None and action == resume_action:
            try:
                self.entry_manager.resume_entry(entry)
                # Update timer widget UI
                self.timer_widget.resume_current()
                # Refresh view
                self._on_date_selected(self.calendar.selectedDate().toPyDate())
            except RuntimeError as e:
                QMessageBox.warning(self, "Error", str(e))
        elif action == delete_action:
            self._delete_entry(entry)
    
    def _edit_entry(self, entry):
        """Open dialog to edit an entry."""
        dialog = EditEntryDialog(entry, self)
        if dialog.exec_() == EditEntryDialog.Accepted:
            if dialog.should_delete:
                self.entry_manager.delete_entry(entry)
            else:
                new_entry = dialog.get_updated_entry()
                self.entry_manager.update_entry(entry, new_entry)
            self._on_date_selected(self.calendar.selectedDate().toPyDate())
    
    def _delete_entry(self, entry):
        """Delete an entry after confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this entry?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted = self.entry_manager.delete_entry(entry)
            if deleted:
                # Offer undo immediately
                undo = QMessageBox.question(
                    self,
                    "Deleted",
                    "Entry deleted. Undo?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if undo == QMessageBox.Yes:
                    restored = self.entry_manager.undo_delete()
                    if restored:
                        QMessageBox.information(self, "Undone", "Entry restored")
            self._on_date_selected(self.calendar.selectedDate().toPyDate())
    
    def _show_manual_entry(self):
        """Show the manual time entry dialog."""
        dialog = ManualEntryDialog(self)
        if dialog.exec_() == ManualEntryDialog.Accepted:
            entry = dialog.get_entry()
            self.entry_manager.add_manual_entry(entry)
            self._on_date_selected(entry.date)

    def _show_export_report(self):
        """Show the report export dialog."""
        dialog = ReportDialog(self.entry_manager, self)
        dialog.exec_()
    
    def _on_exit(self):
        """Handle application exit."""
        if self.entry_manager.current_entry is not None:
            reply = QMessageBox.question(
                self,
                "Timer Running",
                "Timer is still running. Stop it before closing?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.timer_widget.stop_timer()
            else:
                return
        
        self.close()