(() => {
    // Auth elements
    const authModal = document.getElementById('auth_modal');
    const authUsername = document.getElementById('auth_username');
    const authPin = document.getElementById('auth_pin');
    const authError = document.getElementById('auth_error');
    const authLogin = document.getElementById('auth_login');
    const authRegister = document.getElementById('auth_register');
    const currentUserEl = document.getElementById('current_user');
    const logoutBtn = document.getElementById('logout_btn');

    // Elements
    const dateEl = document.getElementById('date');
    const startEl = document.getElementById('start');
    const endEl = document.getElementById('end');
    const descEl = document.getElementById('description');
    const isAbsEl = document.getElementById('is_absence');
    const entriesEl = document.getElementById('entries');
    const addBtn = document.getElementById('add');
    const saveServerBtn = document.getElementById('save_server');
    const loadServerBtn = document.getElementById('load_server');
    const statusEl = document.getElementById('status');
    const exportCsvBtn = document.getElementById('export_csv');
    const themeToggle = document.getElementById('theme_toggle');
    const reportStartEl = document.getElementById('report_start');
    const reportEndEl = document.getElementById('report_end');
    const generateReportBtn = document.getElementById('generate_report');

    // Calendar elements
    const calendarGrid = document.getElementById('calendar_grid');
    const calendarTitle = document.getElementById('calendar_title');
    const calendarPrev = document.getElementById('calendar_prev');
    const calendarNext = document.getElementById('calendar_next');

    // Timer elements
    const timerTimeEl = document.getElementById('timer_time');
    const timerStatusEl = document.getElementById('timer_status');
    const timerDescEl = document.getElementById('timer_description');
    const timerStartBtn = document.getElementById('timer_start');
    const timerStopBtn = document.getElementById('timer_stop');

    // Navigation elements
    const menuToggle = document.getElementById('menu_toggle');
    const mobileMenu = document.getElementById('mobile_menu');
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');

    // Keys
    const ENTRIES_KEY = 'timetracker_entries';
    const RUNNING_KEY = 'timetracker_running';

    // Authentication state
    let isAuthenticated = false;
    let currentUsername = null;
    let serverDbEnabled = false;
    let autoSyncInterval = null;

    // Calendar state
    let currentCalendarDate = new Date();

    // Check authentication status
    async function checkAuth() {
        try {
            const resp = await fetch('/api/auth/status');
            const data = await resp.json();
            if (data.authenticated) {
                isAuthenticated = true;
                currentUsername = data.username;
                showApp();
                // Check if server DB is enabled
                const pingResp = await fetch('/api/ping');
                const pingData = await pingResp.json();
                serverDbEnabled = pingData.server_db_enabled;
                if (serverDbEnabled) {
                    // Load data from server on startup
                    await loadFromServer();
                    // Start auto-sync every 30 seconds
                    startAutoSync();
                }
            } else {
                showAuthModal();
            }
        } catch (err) {
            showAuthModal();
        }
    }

    function startAutoSync() {
        if (autoSyncInterval) clearInterval(autoSyncInterval);
        // Auto-sync every 30 seconds
        autoSyncInterval = setInterval(() => {
            if (isAuthenticated && serverDbEnabled) {
                saveToServer(true); // silent save
            }
        }, 30000);
    }

    function stopAutoSync() {
        if (autoSyncInterval) {
            clearInterval(autoSyncInterval);
            autoSyncInterval = null;
        }
    }

    async function saveToServer(silent = false) {
        if (!isAuthenticated) {
            if (!silent) statusEl.textContent = 'Please login first';
            return;
        }
        const list = loadLocal();
        if (!silent) statusEl.textContent = 'Saving...';
        try {
            const resp = await fetch('/api/save_entries', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify({ entries: list }) 
            });
            const json = await resp.json();
            if (resp.status === 401) {
                if (!silent) statusEl.textContent = 'Session expired. Please login again.';
                showAuthModal();
            } else {
                if (!silent) statusEl.textContent = json.error ? JSON.stringify(json) : `Saved ${json.saved} entries`;
            }
        } catch (err) {
            if (!silent) statusEl.textContent = `Error: ${err}`;
        }
    }

    async function loadFromServer(silent = false) {
        if (!isAuthenticated) {
            if (!silent) statusEl.textContent = 'Please login first';
            return;
        }
        if (!silent) statusEl.textContent = 'Loading...';
        try {
            const resp = await fetch('/api/load_entries');
            const json = await resp.json();
            if (resp.status === 401) {
                if (!silent) statusEl.textContent = 'Session expired. Please login again.';
                showAuthModal();
            } else if (json.entries) {
                saveLocal(json.entries);
                render();
                if (!silent) statusEl.textContent = `Loaded ${json.entries.length} entries`;
            } else {
                if (!silent) statusEl.textContent = JSON.stringify(json);
            }
        } catch (err) {
            if (!silent) statusEl.textContent = `Error: ${err}`;
        }
    }

    function showAuthModal() {
        authModal.setAttribute('aria-hidden', 'false');
        authError.textContent = '';
        stopAutoSync();
    }

    function hideAuthModal() {
        authModal.setAttribute('aria-hidden', 'true');
    }

    function showApp() {
        hideAuthModal();
        currentUserEl.textContent = `👤 ${currentUsername}`;
        logoutBtn.style.display = 'block';
    }

    // Auth handlers
    authLogin.addEventListener('click', async () => {
        const username = authUsername.value.trim();
        const pin = authPin.value.trim();
        
        if (!username || !pin) {
            authError.textContent = 'Please enter username and PIN';
            return;
        }

        try {
            const resp = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, pin })
            });
            const data = await resp.json();
            
            if (resp.ok) {
                isAuthenticated = true;
                currentUsername = data.username;
                showApp();
                authUsername.value = '';
                authPin.value = '';
                
                // Check if server DB is enabled and load data
                const pingResp = await fetch('/api/ping');
                const pingData = await pingResp.json();
                serverDbEnabled = pingData.server_db_enabled;
                if (serverDbEnabled) {
                    await loadFromServer();
                    startAutoSync();
                }
            } else {
                authError.textContent = data.error || 'Login failed';
            }
        } catch (err) {
            authError.textContent = 'Connection error';
        }
    });

    authRegister.addEventListener('click', async () => {
        const username = authUsername.value.trim();
        const pin = authPin.value.trim();
        
        if (!username || !pin) {
            authError.textContent = 'Please enter username and PIN';
            return;
        }

        if (pin.length < 4) {
            authError.textContent = 'PIN must be at least 4 digits';
            return;
        }

        try {
            const resp = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, pin })
            });
            const data = await resp.json();
            
            if (resp.ok) {
                isAuthenticated = true;
                currentUsername = data.username;
                showApp();
                authUsername.value = '';
                authPin.value = '';
                
                // Check if server DB is enabled and load data
                const pingResp = await fetch('/api/ping');
                const pingData = await pingResp.json();
                serverDbEnabled = pingData.server_db_enabled;
                if (serverDbEnabled) {
                    await loadFromServer();
                    startAutoSync();
                }
            } else {
                authError.textContent = data.error || 'Registration failed';
            }
        } catch (err) {
            authError.textContent = 'Connection error';
        }
    });

    logoutBtn.addEventListener('click', async () => {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            isAuthenticated = false;
            currentUsername = null;
            serverDbEnabled = false;
            stopAutoSync();
            logoutBtn.style.display = 'none';
            currentUserEl.textContent = '';
            showAuthModal();
        } catch (err) {
            console.error('Logout error:', err);
        }
    });

    // Allow Enter key to login
    authPin.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            authLogin.click();
        }
    });

    // Theme toggle
    function loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        return savedTheme;
    }

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        console.log('[Theme] Switched to', newTheme);
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // Load saved theme on startup
    loadTheme();

    // View switching
    function switchView(viewName) {
        views.forEach(view => {
            view.classList.remove('active');
        });
        navItems.forEach(item => {
            item.classList.remove('active');
        });
        
        const targetView = document.getElementById(`view_${viewName}`);
        const targetNav = document.querySelector(`[data-view="${viewName}"]`);
        
        if (targetView) targetView.classList.add('active');
        if (targetNav) targetNav.classList.add('active');
        
        // If switching to entries view, render them
        if (viewName === 'entries') {
            render();
        }
    }

    // Navigation handlers
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const view = item.getAttribute('data-view');
            switchView(view);
        });
    });

    menuToggle.addEventListener('click', () => {
        const isHidden = mobileMenu.getAttribute('aria-hidden') === 'true';
        mobileMenu.setAttribute('aria-hidden', !isHidden);
    });

    // Helpers
    function loadLocal() {
        const raw = localStorage.getItem(ENTRIES_KEY);
        const entries = raw ? JSON.parse(raw) : [];
        console.log('[Storage] loadLocal: loaded', entries.length, 'entries');
        return entries;
    }

    function saveLocal(list) {
        console.log('[Storage] saveLocal: saving', list.length, 'entries');
        localStorage.setItem(ENTRIES_KEY, JSON.stringify(list));
        console.log('[Storage] saveLocal: saved successfully');
    }

    function loadRunning() {
        const raw = localStorage.getItem(RUNNING_KEY);
        return raw ? JSON.parse(raw) : null;
    }

    function saveRunning(obj) {
        if (!obj) localStorage.removeItem(RUNNING_KEY);
        else localStorage.setItem(RUNNING_KEY, JSON.stringify(obj));
    }

    function isoToDate(iso) {
        if (!iso) return '';
        return new Date(iso).toISOString().slice(0, 10);
    }

    function isoToTime(iso) {
        if (!iso) return '';
        const d = new Date(iso);
        return d.toTimeString().slice(0, 8);
    }

    function durationSeconds(startIso, endIso) {
        return Math.round((new Date(endIso) - new Date(startIso)) / 1000);
    }

    function formatDuration(sec) {
        const h = Math.floor(sec / 3600).toString().padStart(2, '0');
        const m = Math.floor((sec % 3600) / 60).toString().padStart(2, '0');
        const s = (sec % 60).toString().padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    function fmtEntryCard(e, idx) {
        const wrap = document.createElement('div');
        wrap.className = 'entry-card';
        
        const left = document.createElement('div');
        left.className = 'entry-left';
        
        const meta = document.createElement('div');
        meta.className = 'entry-meta';
        meta.textContent = `${e.date} · ${e.start}–${e.end} ${e.is_absence ? '🏖' : ''}`;
        
        const desc = document.createElement('div');
        desc.textContent = e.description || '(No description)';
        
        left.appendChild(meta);
        left.appendChild(desc);
        
        const actions = document.createElement('div');
        actions.className = 'entry-actions';
        
        // Edit button
        const edit = document.createElement('button');
        edit.textContent = '✏️ Edit';
        edit.addEventListener('click', () => {
            const list = loadLocal();
            // Find the current index of this entry
            const currentIdx = list.findIndex(entry => 
                entry.date === e.date && 
                entry.start === e.start && 
                entry.end === e.end && 
                entry.description === e.description
            );
            if (currentIdx !== -1) {
                openEditModal(e, currentIdx);
            } else {
                alert('Entry not found');
                render();
            }
        });
        actions.appendChild(edit);

        // Resume button (only if entry has start_iso)
        if (e.start_iso) {
            const resumeBtn = document.createElement('button');
            resumeBtn.textContent = '▶️ Resume';
            resumeBtn.addEventListener('click', () => {
                if (loadRunning()) {
                    alert('A timer is already running. Stop it first.');
                    return;
                }
                const list = loadLocal();
                // Find the current index of this entry
                const currentIdx = list.findIndex(entry => 
                    entry.date === e.date && 
                    entry.start === e.start && 
                    entry.end === e.end && 
                    entry.description === e.description
                );
                
                if (currentIdx !== -1) {
                    // remove this entry from storage so stop will re-add updated one
                    list.splice(currentIdx, 1);
                    saveLocal(list);
                }
                
                const running = {
                    start_iso: e.start_iso,
                    description: e.description || ''
                };
                saveRunning(running);
                // start UI timer and switch to timer view
                updateTimerDisplay();
                startTimerInterval();
                switchView('timer');
                render();
            });
            actions.appendChild(resumeBtn);
        }
        
        // Delete button
        const del = document.createElement('button');
        del.textContent = '🗑️ Delete';
        del.addEventListener('click', () => {
            console.log('[Delete] Delete button clicked for entry:', e);
            if (!confirm('Delete this entry?')) {
                console.log('[Delete] User cancelled deletion');
                return;
            }
            
            const list = loadLocal();
            console.log('[Delete] Current list has', list.length, 'entries');
            
            // Find the current index of this entry (in case list changed)
            const currentIdx = list.findIndex(entry => 
                entry.date === e.date && 
                entry.start === e.start && 
                entry.end === e.end && 
                entry.description === e.description
            );
            
            console.log('[Delete] Found entry at index:', currentIdx);
            
            if (currentIdx === -1) {
                console.error('[Delete] Entry not found in list');
                alert('Entry not found');
                render();
                return;
            }
            
            const deleted = list.splice(currentIdx, 1)[0];
            console.log('[Delete] Removed entry:', deleted);
            
            saveLocal(list);
            console.log('[Delete] Saved updated list, now has', list.length, 'entries');
            
            // store last deleted for undo
            sessionStorage.setItem('timetracker_last_deleted', JSON.stringify({ entry: deleted, index: currentIdx }));
            // show undo in status
            showUndoStatus();
            render();
            console.log('[Delete] Re-rendered entries list');
            
            // Auto-save to server if enabled
            if (serverDbEnabled && isAuthenticated) {
                console.log('[Delete] Auto-syncing to server');
                saveToServer(true);
            } else {
                console.log('[Delete] Auto-sync skipped (serverDbEnabled:', serverDbEnabled, 'isAuthenticated:', isAuthenticated, ')');
            }
        });
        actions.appendChild(del);
        
        wrap.appendChild(left);
        wrap.appendChild(actions);
        return wrap;
    }

    function openEditModal(e, idx) {
        const modal = document.getElementById('edit_modal');
        const d = document.getElementById('edit_date');
        const s = document.getElementById('edit_start');
        const en = document.getElementById('edit_end');
        const desc = document.getElementById('edit_description');
        
        // populate with current values
        d.value = e.date || '';
        s.value = e.start || '';
        en.value = e.end || '';
        desc.value = e.description || '';
        modal.setAttribute('aria-hidden', 'false');

        // attach save handler
        const saveBtn = document.getElementById('edit_save');
        const cancelBtn = document.getElementById('edit_cancel');

        function cleanup() {
            saveBtn.removeEventListener('click', onSave);
            cancelBtn.removeEventListener('click', onCancel);
            modal.setAttribute('aria-hidden', 'true');
        }

        function onSave() {
            const list = loadLocal();
            const item = list[idx];
            item.date = d.value;
            item.start = s.value;
            item.end = en.value;
            item.description = desc.value;
            if (item.date && item.start) item.start_iso = `${item.date}T${item.start}`;
            if (item.date && item.end) item.end_iso = `${item.date}T${item.end}`;
            saveLocal(list);
            cleanup();
            render();
            // Auto-save to server if enabled
            if (serverDbEnabled && isAuthenticated) {
                saveToServer(true);
            }
        }

        function onCancel() {
            cleanup();
        }

        saveBtn.addEventListener('click', onSave);
        cancelBtn.addEventListener('click', onCancel);
    }

    function startTimerInterval() {
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(updateTimerDisplay, 1000);
    }

    function showUndoStatus() {
        const raw = sessionStorage.getItem('timetracker_last_deleted');
        if (!raw) {
            statusEl.textContent = '';
            return;
        }
        try {
            const info = JSON.parse(raw);
            statusEl.innerHTML = `Deleted entry. <button id="undo_btn">Undo</button>`;
            const btn = document.getElementById('undo_btn');
            btn.addEventListener('click', () => {
                const list = loadLocal();
                // restore at original index when possible
                const idx = info.index != null && info.index <= list.length ? info.index : list.length;
                list.splice(idx, 0, info.entry);
                saveLocal(list);
                sessionStorage.removeItem('timetracker_last_deleted');
                statusEl.textContent = 'Restored';
                render();
                // Auto-save to server if enabled
                if (serverDbEnabled && isAuthenticated) {
                    saveToServer(true);
                }
            });
        } catch (e) {
            statusEl.textContent = '';
        }
    }

    function renderCalendar() {
        const year = currentCalendarDate.getFullYear();
        const month = currentCalendarDate.getMonth();
        
        // Update title
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        calendarTitle.textContent = `${monthNames[month]} ${year}`;
        
        // Clear grid
        calendarGrid.innerHTML = '';
        
        // Add weekday headers
        const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Week'];
        weekdays.forEach(day => {
            const header = document.createElement('div');
            header.className = 'calendar-weekday';
            header.textContent = day;
            calendarGrid.appendChild(header);
        });
        
        // Calculate hours per day
        const list = loadLocal();
        const hoursPerDay = {};
        
        // Group entries by date
        const entriesByDate = {};
        list.forEach(entry => {
            if (!entry.date) return;
            if (!entriesByDate[entry.date]) {
                entriesByDate[entry.date] = [];
            }
            entriesByDate[entry.date].push(entry);
        });
        
        // Calculate total for each day (work time minus overlapping absences)
        Object.keys(entriesByDate).forEach(date => {
            const entries = entriesByDate[date];
            const workEntries = entries.filter(e => !e.is_absence);
            const absenceEntries = entries.filter(e => e.is_absence);
            
            let totalHours = 0;
            
            // For each work entry, calculate its duration minus overlapping absences
            workEntries.forEach(workEntry => {
                let workStart, workEnd;
                
                if (workEntry.start_iso && workEntry.end_iso) {
                    workStart = new Date(workEntry.start_iso);
                    workEnd = new Date(workEntry.end_iso);
                } else if (workEntry.date && workEntry.start && workEntry.end) {
                    workStart = new Date(`${workEntry.date}T${workEntry.start}`);
                    workEnd = new Date(`${workEntry.date}T${workEntry.end}`);
                } else {
                    return;
                }
                
                let workDuration = (workEnd - workStart) / (1000 * 60 * 60);
                
                // Subtract overlapping absence time
                absenceEntries.forEach(absence => {
                    let absStart, absEnd;
                    
                    if (absence.start_iso && absence.end_iso) {
                        absStart = new Date(absence.start_iso);
                        absEnd = new Date(absence.end_iso);
                    } else if (absence.date && absence.start && absence.end) {
                        absStart = new Date(`${absence.date}T${absence.start}`);
                        absEnd = new Date(`${absence.date}T${absence.end}`);
                    } else {
                        return;
                    }
                    
                    // Calculate overlap
                    const overlapStart = new Date(Math.max(workStart, absStart));
                    const overlapEnd = new Date(Math.min(workEnd, absEnd));
                    
                    if (overlapStart < overlapEnd) {
                        const overlapHours = (overlapEnd - overlapStart) / (1000 * 60 * 60);
                        workDuration -= overlapHours;
                    }
                });
                
                totalHours += workDuration;
            });
            
            hoursPerDay[date] = totalHours;
        });
        
        // Get first day of month (0 = Sunday, 1 = Monday, etc.)
        const firstDay = new Date(year, month, 1);
        let dayOfWeek = firstDay.getDay();
        // Adjust: Monday = 0, Sunday = 6
        dayOfWeek = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
        
        // Get last day of month
        const lastDay = new Date(year, month + 1, 0).getDate();
        
        // Get last day of previous month
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        
        const today = new Date();
        const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        
        let weekHours = 0;
        let dayCount = 0;
        
        // Add previous month's days
        for (let i = dayOfWeek - 1; i >= 0; i--) {
            const day = prevMonthLastDay - i;
            const cell = document.createElement('div');
            cell.className = 'calendar-day other-month';
            cell.innerHTML = `<div class="calendar-day-number">${day}</div>`;
            calendarGrid.appendChild(cell);
            dayCount++;
        }
        
        // Add current month's days
        for (let day = 1; day <= lastDay; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const hours = hoursPerDay[dateStr] || 0;
            weekHours += hours;
            
            const cell = document.createElement('div');
            cell.className = 'calendar-day';
            
            if (dateStr === todayStr) {
                cell.classList.add('today');
            }
            
            if (hours > 0) {
                cell.classList.add('has-entries');
            }
            
            const hoursText = hours > 0 ? `${hours.toFixed(1)}h` : '';
            cell.innerHTML = `
                <div class="calendar-day-number">${day}</div>
                ${hoursText ? `<div class="calendar-day-hours">${hoursText}</div>` : ''}
            `;
            
            cell.addEventListener('click', () => {
                // Filter entries for this day (future feature)
                console.log('Clicked day:', dateStr, 'Hours:', hours);
            });
            
            calendarGrid.appendChild(cell);
            dayCount++;
            
            // Add week total at end of week (Sunday)
            if (dayCount % 7 === 0) {
                const weekTotal = document.createElement('div');
                weekTotal.className = 'calendar-week-total';
                weekTotal.textContent = `${weekHours.toFixed(1)}h`;
                calendarGrid.appendChild(weekTotal);
                weekHours = 0;
            }
        }
        
        // Add next month's days to fill the grid
        const remainingCells = (7 - (dayCount % 7)) % 7;
        for (let day = 1; day <= remainingCells; day++) {
            const cell = document.createElement('div');
            cell.className = 'calendar-day other-month';
            cell.innerHTML = `<div class="calendar-day-number">${day}</div>`;
            calendarGrid.appendChild(cell);
            dayCount++;
        }
        
        // Add final week total if needed
        if (weekHours > 0) {
            const weekTotal = document.createElement('div');
            weekTotal.className = 'calendar-week-total';
            weekTotal.textContent = `${weekHours.toFixed(1)}h`;
            calendarGrid.appendChild(weekTotal);
        }
    }

    function render() {
        console.log('[Render] Starting render');
        
        // Render calendar
        renderCalendar();
        
        // Render entries list
        entriesEl.innerHTML = '';
        const list = loadLocal();
        console.log('[Render] Rendering', list.length, 'entries');
        
        if (list.length === 0) {
            const empty = document.createElement('div');
            empty.style.textAlign = 'center';
            empty.style.padding = '40px 20px';
            empty.style.color = 'var(--text-muted)';
            empty.innerHTML = '<p>No entries yet</p><p style="font-size: 2rem; margin-top: 12px;">📝</p>';
            entriesEl.appendChild(empty);
        } else {
            list.forEach((e, i) => {
                console.log('[Render] Creating card for entry', i, ':', e);
                entriesEl.appendChild(fmtEntryCard(e, i));
            });
        }
        console.log('[Render] Render complete');
    }

    // Timer
    let timerInterval = null;

    function updateTimerDisplay() {
        const running = loadRunning();
        if (!running) {
            timerTimeEl.textContent = '00:00:00';
            timerStatusEl.textContent = 'Stopped';
            timerStartBtn.disabled = false;
            timerStopBtn.disabled = true;
            return;
        }
        const secs = durationSeconds(running.start_iso, new Date().toISOString());
        timerTimeEl.textContent = formatDuration(secs);
        timerStatusEl.textContent = `Running: ${running.description || ''}`;
        timerStartBtn.disabled = true;
        timerStopBtn.disabled = false;
    }

    function startTimer() {
        const desc = (timerDescEl.value || '').trim();
        const now = new Date();
        const running = {
            start_iso: now.toISOString(),
            description: desc,
        };
        saveRunning(running);
        updateTimerDisplay();
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(updateTimerDisplay, 1000);
    }

    function stopTimer() {
        const running = loadRunning();
        if (!running) return;
        const endIso = new Date().toISOString();
        const entry = {
            date: isoToDate(running.start_iso),
            start: isoToTime(running.start_iso),
            end: isoToTime(endIso),
            description: running.description || '',
            is_absence: false,
            start_iso: running.start_iso,
            end_iso: endIso,
        };
        const list = loadLocal();
        list.push(entry);
        saveLocal(list);
        saveRunning(null);
        if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
        timerDescEl.value = '';
        updateTimerDisplay();
        render();
        // Auto-save to server if enabled
        if (serverDbEnabled && isAuthenticated) {
            saveToServer(true);
        }
    }

    timerStartBtn.addEventListener('click', () => startTimer());
    timerStopBtn.addEventListener('click', () => stopTimer());

    // Manual add
    addBtn.addEventListener('click', () => {
        const e = {
            date: dateEl.value,
            start: startEl.value,
            end: endEl.value,
            description: descEl.value || '',
            is_absence: !!isAbsEl.checked,
        };
        if (!e.date || !e.start || !e.end) {
            alert('Please fill in date, start time, and end time');
            return;
        }
        // Add ISO timestamps for duration calculations
        e.start_iso = `${e.date}T${e.start}`;
        e.end_iso = `${e.date}T${e.end}`;
        
        const list = loadLocal();
        list.push(e);
        saveLocal(list);
        // Clear form
        descEl.value = '';
        isAbsEl.checked = false;
        // Show success and switch to entries view
        statusEl.textContent = 'Entry added successfully!';
        setTimeout(() => { statusEl.textContent = ''; }, 2000);
        switchView('entries');
        render();
        // Auto-save to server if enabled
        if (serverDbEnabled && isAuthenticated) {
            saveToServer(true);
        }
    });

    saveServerBtn.addEventListener('click', () => saveToServer(false));
    loadServerBtn.addEventListener('click', () => loadFromServer(false));

    // Calendar navigation
    if (calendarPrev) {
        calendarPrev.addEventListener('click', () => {
            currentCalendarDate.setMonth(currentCalendarDate.getMonth() - 1);
            renderCalendar();
        });
    }

    if (calendarNext) {
        calendarNext.addEventListener('click', () => {
            currentCalendarDate.setMonth(currentCalendarDate.getMonth() + 1);
            renderCalendar();
        });
    }

    // Export to CSV
    if (exportCsvBtn) {
        console.log('[Export] Export CSV button found and initialized');
        exportCsvBtn.addEventListener('click', () => {
            console.log('[Export] Export button clicked');
            const list = loadLocal();
            console.log('[Export] Loaded entries from localStorage:', list.length, 'entries');
            
            if (list.length === 0) {
                console.warn('[Export] No entries to export');
                alert('No entries to export');
                return;
            }

            // Create CSV content
            let csv = 'Date,Start Time,End Time,Duration (hours),Description,Type\n';
            console.log('[Export] CSV header created');
            
            // Sort entries by date and start time
            const sortedList = [...list].sort((a, b) => {
                const dateCompare = (a.date || '').localeCompare(b.date || '');
                if (dateCompare !== 0) return dateCompare;
                return (a.start || '').localeCompare(b.start || '');
            });
            console.log('[Export] Entries sorted');

            sortedList.forEach((e, idx) => {
                const date = e.date || '';
                const start = e.start || '';
                const end = e.end || '';
                const description = (e.description || '').replace(/"/g, '""'); // Escape quotes
                const type = e.is_absence ? 'Absence' : 'Work';
                
                // Calculate duration in hours
                let duration = 0;
                if (date && start && end) {
                    try {
                        // Build ISO strings if they don't exist
                        const startIso = e.start_iso || `${date}T${start}`;
                        const endIso = e.end_iso || `${date}T${end}`;
                        const startTime = new Date(startIso);
                        const endTime = new Date(endIso);
                        const diffMs = endTime - startTime;
                        duration = (diffMs / (1000 * 60 * 60)).toFixed(2);
                        console.log(`[Export] Entry ${idx + 1}: ${date} ${start}-${end} = ${duration}h`);
                    } catch (err) {
                        console.error(`[Export] Error calculating duration for entry ${idx + 1}:`, err, e);
                        duration = 0;
                    }
                } else {
                    console.warn(`[Export] Entry ${idx + 1} missing date/start/end:`, e);
                }
                
                csv += `${date},${start},${end},${duration},"${description}",${type}\n`;
            });

            console.log('[Export] CSV content created, length:', csv.length, 'bytes');

            // Create download link
            try {
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                console.log('[Export] Blob created, size:', blob.size, 'bytes');
                
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                const filename = `timetracker_export_${new Date().toISOString().slice(0, 10)}.csv`;
                console.log('[Export] Download filename:', filename);
                
                link.setAttribute('href', url);
                link.setAttribute('download', filename);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                console.log('[Export] Download link created and added to DOM');
                
                link.click();
                console.log('[Export] Download link clicked');
                
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                console.log('[Export] Cleanup complete');
                
                statusEl.textContent = `Exported ${list.length} entries to ${filename}`;
                setTimeout(() => { statusEl.textContent = ''; }, 3000);
                console.log('[Export] Export completed successfully');
            } catch (err) {
                console.error('[Export] Error creating download:', err);
                alert('Error creating CSV download: ' + err.message);
            }
        });
    } else {
        console.error('[Export] Export CSV button not found in DOM');
    }

    // Generate Report
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', () => {
            const startDate = reportStartEl.value;
            const endDate = reportEndEl.value;
            
            if (!startDate || !endDate) {
                alert('Please select both start and end dates');
                return;
            }
            
            if (startDate > endDate) {
                alert('Start date must be before end date');
                return;
            }
            
            const list = loadLocal();
            
            // Filter entries within date range
            const filteredEntries = list.filter(e => e.date >= startDate && e.date <= endDate);
            
            if (filteredEntries.length === 0) {
                alert('No entries found in the selected date range');
                return;
            }
            
            // Generate date range
            const dates = [];
            const current = new Date(startDate);
            const end = new Date(endDate);
            
            while (current <= end) {
                const dateStr = current.toISOString().slice(0, 10);
                dates.push(dateStr);
                current.setDate(current.getDate() + 1);
            }
            
            // Group entries by date
            const entriesByDate = {};
            filteredEntries.forEach(entry => {
                if (!entry.date) return;
                if (!entriesByDate[entry.date]) {
                    entriesByDate[entry.date] = [];
                }
                entriesByDate[entry.date].push(entry);
            });
            
            // Calculate hours per day (work minus overlapping absences)
            const hoursPerDay = {};
            Object.keys(entriesByDate).forEach(date => {
                const entries = entriesByDate[date];
                const workEntries = entries.filter(e => !e.is_absence);
                const absenceEntries = entries.filter(e => e.is_absence);
                
                let totalHours = 0;
                
                workEntries.forEach(workEntry => {
                    let workStart, workEnd;
                    
                    if (workEntry.start_iso && workEntry.end_iso) {
                        workStart = new Date(workEntry.start_iso);
                        workEnd = new Date(workEntry.end_iso);
                    } else if (workEntry.date && workEntry.start && workEntry.end) {
                        workStart = new Date(`${workEntry.date}T${workEntry.start}`);
                        workEnd = new Date(`${workEntry.date}T${workEntry.end}`);
                    } else {
                        return;
                    }
                    
                    let workDuration = (workEnd - workStart) / (1000 * 60 * 60);
                    
                    absenceEntries.forEach(absence => {
                        let absStart, absEnd;
                        
                        if (absence.start_iso && absence.end_iso) {
                            absStart = new Date(absence.start_iso);
                            absEnd = new Date(absence.end_iso);
                        } else if (absence.date && absence.start && absence.end) {
                            absStart = new Date(`${absence.date}T${absence.start}`);
                            absEnd = new Date(`${absence.date}T${absence.end}`);
                        } else {
                            return;
                        }
                        
                        const overlapStart = new Date(Math.max(workStart, absStart));
                        const overlapEnd = new Date(Math.min(workEnd, absEnd));
                        
                        if (overlapStart < overlapEnd) {
                            const overlapHours = (overlapEnd - overlapStart) / (1000 * 60 * 60);
                            workDuration -= overlapHours;
                        }
                    });
                    
                    totalHours += workDuration;
                });
                
                hoursPerDay[date] = totalHours;
            });
            
            // Create CSV with daily and weekly totals
            let csv = 'Date,Day,Hours Worked\n';
            let weekHours = 0;
            let weekNumber = 1;
            const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            
            dates.forEach((dateStr, idx) => {
                const date = new Date(dateStr + 'T00:00:00');
                const dayName = dayNames[date.getDay()];
                const hours = hoursPerDay[dateStr] || 0;
                weekHours += hours;
                
                csv += `${dateStr},${dayName},${hours.toFixed(2)}\n`;
                
                // Add week total on Sunday or last day
                if (date.getDay() === 0 || idx === dates.length - 1) {
                    csv += `,,Week ${weekNumber} Total: ${weekHours.toFixed(2)}h\n`;
                    weekHours = 0;
                    weekNumber++;
                    csv += '\n'; // Add blank line between weeks
                }
            });
            
            // Add grand total
            const grandTotal = Object.values(hoursPerDay).reduce((sum, h) => sum + h, 0);
            csv += `,,Grand Total: ${grandTotal.toFixed(2)}h\n`;
            
            // Download report
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            const filename = `timetracker_report_${startDate}_to_${endDate}.csv`;
            
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            statusEl.textContent = `Report generated: ${filteredEntries.length} entries, ${grandTotal.toFixed(2)} hours total`;
            setTimeout(() => { statusEl.textContent = ''; }, 5000);
        });
    }

    // initialize date input with today
    const now = new Date();
    dateEl.value = now.toISOString().slice(0, 10);

    // initialize timer state
    if (loadRunning()) {
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(updateTimerDisplay, 1000);
    }
    updateTimerDisplay();
    render();
    showUndoStatus();
    
    // Initialize report date inputs with current month
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    if (reportStartEl) reportStartEl.value = firstDay.toISOString().slice(0, 10);
    if (reportEndEl) reportEndEl.value = lastDay.toISOString().slice(0, 10);
    
    // Check authentication on startup
    checkAuth();
})();
