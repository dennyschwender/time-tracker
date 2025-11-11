# TimeTracking

Simple cross-platform time tracking GUI application (PyQt5).

## Requirements

- Python 3.11+
- Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
## TimeTracking

TimeTracking is a small cross-platform time-tracking application. It includes:

- A desktop PyQt5 GUI (timer, manual entries, edit/delete, Excel export)
- A lightweight web frontend (SPA) with optional server persistence (Flask + SQLite)

This README shows how to set up and run the desktop app and the webapp, run tests, and package the project.

## Features

Key features available in both the desktop and web apps:

- Resume: continue an existing entry instead of creating a new one. Useful if you stopped tracking and want to continue the same task — the running timer will extend the original entry rather than creating a duplicate.

- Edit: modify an existing entry's date, start/end times, and description. The desktop app provides an Edit dialog; the webapp offers an Edit modal for quick fixes.

- Undo / Confirm Delete: deletions require confirmation. An immediate Undo is available for accidental deletions — desktop uses a one-step undo in the manager, the webapp stores the last deletion in the session and presents an Undo action in the UI.

These behaviors are documented here so you can discover them quickly when using either interface.

## Requirements

- Python 3.11+
- A POSIX shell for the examples below (macOS / Linux). Windows PowerShell equivalents are shown where relevant.

Recommended: create and use a virtual environment in the project root:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# On Windows (PowerShell): .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Note: the `webapp` directory has its own lightweight dependencies (Flask, gunicorn). You can use the same venv or install from `webapp/requirements.txt`.

## Desktop application (PyQt)

Run the desktop GUI from the `TimeTracking` directory:

```bash
# from project root (TimeTracking)
.venv/bin/python src/main.py
```

Windows (PowerShell):

```powershell
$env:PYTHONPATH = "./src"; .\.venv\Scripts\python.exe src\main.py
```

Environment variables of interest:

- `TIMETRACKER_DEBUG=1` — enable debug prints used during development

Data storage:

The desktop app uses `appdirs` to choose a platform-appropriate user data directory. The JSON file is named `timedata.json` and is stored under the standard app data folder for your OS (e.g. `~/Library/Application Support/TimeTracker` on macOS).

Export:

Use File -> Export Report... in the app to generate an Excel `.xlsx` report for a date range.

## Web application (SPA + Flask)

The web UI is a single-page app (static) served by a small Flask backend. By default the client stores everything in browser `localStorage`. Server-side persistence is optional and controlled by an environment variable.

Run the webapp (development server):

```bash
cd webapp
. ../.venv/bin/activate   # if not already active
../.venv/bin/python app.py
```

By default the server listens on port `5000`. You can override the port with `PORT` env var and enable server DB persistence with `USE_SERVER_DB=1`.

Examples:

```bash
# run on port 5001
PORT=5001 ../.venv/bin/python app.py

# enable server-side SQLite persistence
USE_SERVER_DB=1 ../.venv/bin/python app.py
```

Notes:

- Server DB: when `USE_SERVER_DB=1` the server stores entries in `web_data.db` inside the platform-appropriate app data dir (via `appdirs`).
- Client storage: the SPA keeps a copy in `localStorage`, and syncs to the server only when you press "Sync to Server".

Docker (optional): a Dockerfile and `docker-compose.yml` are included for the webapp. From the repository root you can run:

```bash
docker compose up --build
```

This runs the web service in a container and exposes it on the port configured in the compose file (check `docker-compose.yml`).

## Tests

Run the Python unit tests with pytest from the project root:

```bash
.venv/bin/python -m pytest -q
```

Run only the webapp unit tests:

```bash
cd webapp
. ../.venv/bin/activate
../.venv/bin/python -m pytest -q
```

Playwright / E2E:

An optional Playwright test is included under `webapp/tests/e2e/` but it is skipped by default. To run E2E tests you must install Playwright and browsers:

```bash
pip install playwright pytest-playwright
npx playwright install  # or: playwright install
```

Then start the webapp and run the E2E test (example):

```bash
# start webapp
cd webapp
../.venv/bin/python app.py

# in another terminal
cd webapp
../.venv/bin/python -m pytest tests/e2e/test_timer_resume.py -q
```

## Development notes

- Code layout (top-level `src/`):

```text
src/
├── gui/           # PyQt GUI widgets and dialogs
├── models/        # TimeEntry and TimeEntryManager
└── utils/         # helper utilities
```

- The `webapp/` folder contains a small Flask app (`webapp/app.py`) and a static SPA under `webapp/static/`.
- Tests live under `tests/` (desktop) and `webapp/tests/` (web).

## Troubleshooting

- If the desktop app fails to start because `PyQt5` is missing: ensure you installed `PyQt5` in the venv and use the Python executable from that venv.
- If the webapp returns `"server persistence disabled"` when calling `/api/save_entries` or `/api/load_entries`, set `USE_SERVER_DB=1` before starting the server.
- If port 5000 is in use, change `PORT` when running `app.py`.

## License

MIT License
