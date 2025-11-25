#!/usr/bin/env python3
"""CLI entry point for the TimeTracking data model."""

import argparse
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from appdirs import user_data_dir

from models.entry_manager import TimeEntryManager
from models.time_entry import TimeEntry
from utils.remote_client import RemoteTimeTrackerClient
from utils.time_utils import format_duration

APP_NAME = "TimeTracker"
APP_AUTHOR = "dennyschwender"
DEFAULT_FILENAME = "timedata.json"


def find_storage_path(custom_path: Optional[Path]) -> Path:
    """Return the storage file path, honoring an explicit override if provided."""
    if custom_path:
        custom_path.parent.mkdir(parents=True, exist_ok=True)
        return custom_path

    candidates = [
        Path(user_data_dir(APP_NAME, APP_AUTHOR)) / DEFAULT_FILENAME,
        Path.home() / ".timetracker" / "timedata.json",
        Path.home() / ".timetracker" / "data" / "timedata.json",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    default = candidates[0]
    default.parent.mkdir(parents=True, exist_ok=True)
    return default


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'; use YYYY-MM-DD format."
        )


def parse_iso_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime '{value}'; use YYYY-MM-DDTHH:MM:SS format."
        )


def sorted_entries(entries: List[TimeEntry]) -> List[TimeEntry]:
    return sorted(entries, key=lambda entry: entry.start_time)


def format_entry(entry: TimeEntry, index: Optional[int] = None) -> str:
    label = f"[{index}] " if index is not None else ""
    duration = format_duration(entry.duration)
    flags = " [ABSENCE]" if entry.is_absence else ""
    lines = [
        f"{label}{entry.start_time.isoformat()} -> {entry.end_time.isoformat()} ({duration}){flags}"
    ]
    if entry.description:
        lines.append(f"    {entry.description}")
    return "\n".join(lines)


def print_entries_for_date(manager: TimeEntryManager, target: date) -> None:
    entries = sorted_entries(manager.get_entries_for_date(target))
    print(f"Entries for {target.isoformat()}: {len(entries)}")
    if not entries:
        print("  (none)")
        return

    for idx, entry in enumerate(entries, start=1):
        print(format_entry(entry, idx))


def command_start(manager: TimeEntryManager, args: argparse.Namespace) -> None:
    try:
        manager.start_timer(args.description or "")
        print("Timer started.")
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def command_stop(manager: TimeEntryManager, args: argparse.Namespace) -> None:
    if manager.current_entry is None:
        print("No timer running.", file=sys.stderr)
        sys.exit(1)

    entry = manager.current_entry
    manager.stop_timer()
    print("Timer stopped.")
    print(format_entry(entry))


def command_status(manager: TimeEntryManager, args: argparse.Namespace) -> None:
    today = date.today()
    if manager.current_entry:
        print("Timer is running:")
        print(format_entry(manager.current_entry))
    else:
        print("No timer running.")

    total = manager.get_total_time_for_date(today)
    entries = manager.get_entries_for_date(today)
    print(
        f"Today ({today.isoformat()}): {len(entries)} entry(s), total {format_duration(total)}"
    )


def command_list(manager: TimeEntryManager, args: argparse.Namespace) -> None:
    target = args.date or date.today()
    print_entries_for_date(manager, target)


def command_add(manager: TimeEntryManager, args: argparse.Namespace) -> None:
    start = parse_iso_datetime(args.start)
    end = parse_iso_datetime(args.end)
    if end <= start:
        print("End time must be after start time.", file=sys.stderr)
        sys.exit(1)

    entry = TimeEntry(
        start_time=start,
        end_time=end,
        description=args.description or "",
        is_absence=args.absence,
    )
    manager.add_manual_entry(entry)
    print("Manual entry added:")
    print(format_entry(entry))


def command_resume(manager: TimeEntryManager, args: argparse.Namespace) -> None:
    target = args.date or date.today()
    entries = sorted_entries(manager.get_entries_for_date(target))
    if not entries:
        print(f"No entries found for {target.isoformat()}.", file=sys.stderr)
        sys.exit(1)

    if args.index < 1 or args.index > len(entries):
        print("Index out of range.", file=sys.stderr)
        sys.exit(1)

    entry = entries[args.index - 1]
    if entry.is_absence:
        print("Cannot resume an absence entry.", file=sys.stderr)
        sys.exit(1)

    try:
        manager.resume_entry(entry)
        print("Resumed entry:")
        print(format_entry(entry))
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def command_report(manager: TimeEntryManager, args: argparse.Namespace) -> None:
    start = args.start_date or date.today()
    end = args.end_date or start
    dates, descriptions, matrix = manager.generate_report(start, end)

    if not descriptions:
        print("No entries in the requested range.")
        return

    header_dates = [d.isoformat() for d in dates]
    max_desc = max(len(desc) for desc in descriptions)
    label_width = max(12, max_desc + 2)

    header = "Description".ljust(label_width) + " ".join(
        f"{d:^10}" for d in header_dates
    )
    separator = "-" * len(header)
    print(header)
    print(separator)

    for desc in descriptions:
        values = matrix.get(desc, [])
        formatted = "".join(f"{value:10.2f}" for value in values)
        print(desc.ljust(label_width) + formatted)


def _all_saved_entries(manager: TimeEntryManager) -> List[TimeEntry]:
    entries: List[TimeEntry] = []
    for daily_entries in manager.entries.values():
        entries.extend(daily_entries)
    return entries


def command_sync(manager: TimeEntryManager, args: argparse.Namespace) -> None:
    server_url = args.server_url or os.getenv("TIMETRACKER_REMOTE_URL")
    username = args.username or os.getenv("TIMETRACKER_REMOTE_USERNAME")
    pin = args.pin or os.getenv("TIMETRACKER_REMOTE_PIN")

    if not server_url:
        print("--server-url is required for sync operations.", file=sys.stderr)
        sys.exit(1)

    if not username or not pin:
        print("Username and PIN are required to authenticate with the remote server.", file=sys.stderr)
        sys.exit(1)

    client = RemoteTimeTrackerClient(server_url)
    try:
        client.login(username, pin)
    except Exception as exc:  # pragma: no cover
        print(f"Failed to authenticate with remote server: {exc}", file=sys.stderr)
        client.close()
        sys.exit(1)

    try:
        if args.direction in ("push", "both"):
            local_entries = _all_saved_entries(manager)
            result = client.save_entries(local_entries)
            saved = result.get("saved")
            print(f"Pushed {saved or 0} entries to {server_url}")

        if args.direction in ("pull", "both"):
            remote_entries = client.load_entries()
            manager.replace_entries(remote_entries)
            print(f"Pulled {len(remote_entries)} entries from {server_url}")
    except Exception as exc:  # pragma: no cover
        print(f"Failed to sync with remote server: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage TimeTracker entries from the command line."
    )
    parser.add_argument(
        "--storage",
        type=Path,
        help="Explicit path to the timedata.json file.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Start the timer.")
    start.add_argument("--description", help="Optional description for the timer.")

    subparsers.add_parser("stop", help="Stop the running timer.")
    subparsers.add_parser("status", help="Show timer status and today's total.")

    cmd_list = subparsers.add_parser("list", help="List entries for a date.")
    cmd_list.add_argument(
        "--date", type=parse_iso_date, help="Date to list (YYYY-MM-DD)."
    )

    add = subparsers.add_parser("add", help="Add a manual entry via start/end.")
    add.add_argument(
        "--start",
        required=True,
        help="Start timestamp (YYYY-MM-DDTHH:MM:SS).",
    )
    add.add_argument(
        "--end",
        required=True,
        help="End timestamp (YYYY-MM-DDTHH:MM:SS).",
    )
    add.add_argument("--description", help="Description text.")
    add.add_argument(
        "--absence", action="store_true", help="Mark the entry as an absence."
    )

    resume = subparsers.add_parser("resume", help="Resume an existing entry.")
    resume.add_argument(
        "--date",
        type=parse_iso_date,
        help="Date containing the entry to resume.",
    )
    resume.add_argument(
        "--index",
        type=int,
        default=1,
        help="1-based index from the list command.",
    )

    report = subparsers.add_parser("report", help="Show a tabular report.")
    report.add_argument(
        "--start-date",
        type=parse_iso_date,
        help="Start date for the report range (YYYY-MM-DD).",
    )
    report.add_argument(
        "--end-date",
        type=parse_iso_date,
        help="End date for the report range (YYYY-MM-DD).",
    )

    sync = subparsers.add_parser("sync", help="Push/pull entries to the remote webapp.")
    sync.add_argument(
        "--direction",
        choices=["push", "pull", "both"],
        default="both",
        help="Which direction to sync entries (default: both).",
    )
    sync.add_argument(
        "--server-url",
        help="Remote webapp base URL (can be set via TIMETRACKER_REMOTE_URL).",
    )
    sync.add_argument(
        "--username",
        help="Remote username (can also be set via TIMETRACKER_REMOTE_USERNAME).",
    )
    sync.add_argument(
        "--pin",
        help="Remote PIN (can also be set via TIMETRACKER_REMOTE_PIN).",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    storage_path = find_storage_path(getattr(args, "storage", None))
    manager = TimeEntryManager(storage_path)

    commands = {
        "start": command_start,
        "stop": command_stop,
        "status": command_status,
        "list": command_list,
        "add": command_add,
        "resume": command_resume,
        "report": command_report,
        "sync": command_sync,
    }

    handler = commands.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    handler(manager, args)


if __name__ == "__main__":
    main()
