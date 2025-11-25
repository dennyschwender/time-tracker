# TimeTracking

TimeTracking is a lightweight, cross-platform **command-line** time tracker backed by a shared data model that can also power the companion Flask-based webapp under `webapp/`.

## Requirements

- Python 3.11 or later
- A POSIX shell for the commands below (macOS / Linux, PowerShell equivalents work on Windows)
- Create and activate a virtual environment from the project root:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

## CLI Usage

The CLI entry point is `src/main.py`. You can use the following commands:

- `python src/main.py start [--description "Work description"]` — starts a new timer (fails if the timer is already running).
- `python src/main.py stop` — stops the running timer and records the entry.
- `python src/main.py status` — shows whether a timer is running and the total for today.
- `python src/main.py list [--date YYYY-MM-DD]` — lists stored entries for the given date (defaults to today).
- `python src/main.py add --start YYYY-MM-DDTHH:MM:SS --end YYYY-MM-DDTHH:MM:SS [--description TEXT] [--absence]` — adds a manual entry.
- `python src/main.py resume [--date YYYY-MM-DD] [--index N]` — resumes an existing (non-absence) entry using the 1-based index from `list`.
- `python src/main.py report [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]` — prints a tabular report for the requested range.
- `python src/main.py sync [--direction push|pull|both] --server-url <URL> --username <user> --pin <pin>` — synchronize the local storage with a running webapp instance so the CLI and webapp share the same entries. Defaults to pushing local entries and pulling any changes (`both`).

The sync command accepts `TIMETRACKER_REMOTE_URL`, `TIMETRACKER_REMOTE_USERNAME`, and `TIMETRACKER_REMOTE_PIN` environment variables if you prefer not to pass credentials on the command line (you still need to supply `--server-url` or set `TIMETRACKER_REMOTE_URL`).

Each command accepts `--storage /path/to/timedata.json` to override the default storage file if needed. The CLI relies on the same `TimeEntryManager` code that was previously used by the GUI, so existing JSON files will continue to load.

## Data Storage

Entries are stored in `timedata.json` inside the platform-appropriate app data directory determined by `appdirs`. On macOS this is `~/Library/Application Support/TimeTracker/timedata.json`, and Linux uses `~/.local/share/TimeTracker`. Legacy files under `~/.timetracker/` are still supported. The CLI will create the folder structure automatically.

## Web Application (SPA + Flask)

The `webapp/` directory still hosts the Flask-backed single-page application. Copy `.env.example` to `.env`, set the secret key, and enable server persistence (if desired) while keeping the CLI data in sync:

```bash
cp .env.example .env
# edit SECRET_KEY, USE_SERVER_DB, PORT, etc.
```

Run the webapp locally:

```bash
cd webapp
source ../.venv/bin/activate  # if not already active
python app.py
```

The SPA requires authentication via username + PIN, stores a local copy in the browser, and optionally syncs to the server when `USE_SERVER_DB=1`.

Docker Compose (optional):

```bash
docker compose up --build
```

## Tests

Run the unit tests from the project root:

```bash
.venv/bin/python -m pytest -q
```

For the webapp tests, change directory to `webapp/` and run pytest via the shared venv:

```bash
cd webapp
../.venv/bin/python -m pytest -q
```

## Troubleshooting

- If the CLI complains about the storage path, confirm the parent directory is writable or pass `--storage` to point to another file.
- You can set `TIMETRACKER_DEBUG=1` in your shell before running the CLI to see debug prints from the entry manager.
- If the webapp reports "server persistence disabled", set `USE_SERVER_DB=1` before starting the Flask server.

## License

MIT License
