# TimeTracking Feature Alignment

This document tracks feature parity between the Desktop (PyQt5) and Web versions.

## ✅ Aligned Features

### Core Functionality

- [x] **Timer** - Start/Stop timer with description
- [x] **Manual Entry** - Add entries with date, start, end, description
- [x] **Absence Tracking** - Mark entries as absences
- [x] **Entry Management** - Edit, Delete, Resume entries
- [x] **Calendar View** - Monthly calendar with daily totals
- [x] **Weekly Totals** - Show total hours per week
- [x] **Absence Overlap Calculation** - Absences only subtract from overlapping work time
- [x] **Export** - Export to CSV (Desktop: Excel, Web: CSV)
- [x] **Data Persistence** - Local storage (Desktop: JSON, Web: localStorage + optional server DB)

### Entry Display

- [x] **Entry List** - View all entries for selected date
- [x] **Sort by Time** - Entries sorted by start time
- [x] **Visual Indicators** - Absences marked with emoji 🏖

### User Experience

- [x] **Mobile Responsive** - Web version is mobile-friendly
- [x] **Today Highlighting** - Current date highlighted in calendar
- [x] **Entry Cards** - Organized display with metadata

## ⚠️ Desktop-Only Features

### Desktop Exclusive

- [ ] **Theme Selection** - Dark/Light theme switcher
- [ ] **Export to Excel** - .xlsx format (Web: CSV only)
- [ ] **Context Menu** - Right-click on entries
- [ ] **Date Range Report** - Generate reports for custom date ranges
- [ ] **Calendar Day Highlighting** - Days with entries highlighted in calendar widget
- [ ] **Status Bar** - Shows application status messages
- [ ] **Native File Dialogs** - System file picker for exports
- [ ] **Desktop Notifications** - System tray notifications (if implemented)

## ⚠️ Web-Only Features

### Web Exclusive

- [x] **Multi-User Authentication** - Username + PIN authentication
- [x] **Server Sync** - Automatic sync to server database (optional)
- [x] **Auto-Sync** - Background sync every 30 seconds
- [x] **Session Management** - 7-day persistent sessions
- [x] **Undo Delete** - Quick undo for deleted entries
- [x] **Bottom Navigation** - Mobile-optimized navigation
- [x] **Docker Deployment** - Containerized deployment option
- [x] **Environment Variables** - .env configuration

## 🔄 Features to Align

### High Priority

1. **✅ COMPLETED - Export Format Alignment**
   - [x] Web: CSV export with date range reports
   - [x] Desktop: Excel export already exists

2. **✅ COMPLETED - Theme Support**
   - [x] Web: Dark/light theme toggle added
   - [x] Desktop: Already has theme support

3. **✅ COMPLETED - Calendar Features**
   - [x] Desktop: Added weekly totals to calendar display
   - [x] Web: Already has weekly totals in calendar grid

4. **✅ COMPLETED - Date Range Reports**
   - [x] Web: Added date range report generation
   - [x] Desktop: Already has report dialog

### Medium Priority

5. **Entry Filtering**
   - [ ] Both: Add search/filter by description
   - [ ] Web: Add ability to click calendar day to filter entries

6. **Calendar Day Click**
   - [x] Web: Calendar days are clickable (ready for filtering)
   - [x] Desktop: Already selects and shows entries for day

7. **Resume Timer**
   - [x] Both: Already implemented

### Low Priority
8. **Visual Enhancements**
   - [ ] Desktop: Match web's card-based entry display
   - [ ] Web: Add more visual feedback

9. **Entry Statistics**
   - [ ] Both: Add statistics view (weekly/monthly summaries)

## 📝 Implementation Notes

### Absence Calculation
Both versions now correctly implement:
- Absences only subtract from overlapping work entries
- Non-overlapping absences have no effect on totals
- Overlap calculation uses min/max of start/end times

### Data Storage
- **Desktop**: Single JSON file in platform-specific data directory
- **Web**: localStorage + optional server-side SQLite database

### Export Functionality
- **Desktop**: Excel (.xlsx) with formatted cells, auto-width columns
- **Web**: CSV with proper escaping, includes duration calculation

## 🎯 Recommended Next Steps

1. Add theme toggle to web version (CSS variables already in place)
2. Implement date range filtering on both versions
3. Add date range report to web version
4. Consider unified data format for easier migration between versions
5. Add more comprehensive statistics/analytics view

## 🔧 Technical Debt

- Web: Remove console.log statements before production
- Desktop: Consider adding web's undo functionality
- Both: Add unit tests for overlap calculations
- Both: Add data import/export between versions

---

Last Updated: 2025-11-17
