(() => {
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
        return raw ? JSON.parse(raw) : [];
    }

    function saveLocal(list) {
        localStorage.setItem(ENTRIES_KEY, JSON.stringify(list));
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
            openEditModal(e, idx);
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
                // remove this entry from storage so stop will re-add updated one
                list.splice(idx, 1);
                saveLocal(list);
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
            if (!confirm('Delete this entry?')) return;
            const list = loadLocal();
            const deleted = list.splice(idx, 1)[0];
            saveLocal(list);
            // store last deleted for undo
            sessionStorage.setItem('timetracker_last_deleted', JSON.stringify({ entry: deleted, index: idx }));
            // show undo in status
            showUndoStatus();
            render();
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
            });
        } catch (e) {
            statusEl.textContent = '';
        }
    }

    function render() {
        entriesEl.innerHTML = '';
        const list = loadLocal();
        if (list.length === 0) {
            const empty = document.createElement('div');
            empty.style.textAlign = 'center';
            empty.style.padding = '40px 20px';
            empty.style.color = 'var(--text-muted)';
            empty.innerHTML = '<p>No entries yet</p><p style="font-size: 2rem; margin-top: 12px;">📝</p>';
            entriesEl.appendChild(empty);
        } else {
            list.forEach((e, i) => entriesEl.appendChild(fmtEntryCard(e, i)));
        }
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
    });

    saveServerBtn.addEventListener('click', async () => {
        const list = loadLocal();
        statusEl.textContent = 'Saving...';
        try {
            const resp = await fetch('/api/save_entries', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ entries: list }) });
            const json = await resp.json();
            statusEl.textContent = json.error ? JSON.stringify(json) : `Saved ${json.saved}`;
        } catch (err) {
            statusEl.textContent = `Error: ${err}`;
        }
    });

    loadServerBtn.addEventListener('click', async () => {
        statusEl.textContent = 'Loading...';
        try {
            const resp = await fetch('/api/load_entries');
            const json = await resp.json();
            if (json.entries) {
                saveLocal(json.entries);
                render();
                statusEl.textContent = `Loaded ${json.entries.length}`;
            } else {
                statusEl.textContent = JSON.stringify(json);
            }
        } catch (err) {
            statusEl.textContent = `Error: ${err}`;
        }
    });

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
})();
