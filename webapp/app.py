from pathlib import Path
import os
import json
from flask import Flask, send_from_directory, request, jsonify, render_template
from appdirs import user_data_dir
import sqlite3

APPNAME = "TimeTrackerWeb"
APPAUTHOR = "dennyschwender"

app = Flask(__name__, static_folder="static", template_folder="templates")


# Error handlers to ensure JSON responses instead of HTML
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


def get_db_path() -> Path:
    data_dir = Path(user_data_dir(APPNAME, APPAUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "web_data.db"


def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            start TEXT,
            end TEXT,
            description TEXT,
            is_absence INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


# Initialize database on app startup
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ping")
def ping():
    return jsonify({"ok": True})


@app.route("/api/save_entries", methods=["POST"])
def save_entries():
    # optional server-side persistence; if disabled by env var, return 403
    if os.getenv("USE_SERVER_DB", "0") != "1":
        return jsonify({"error": "server persistence disabled"}), 403
    try:
        data = request.get_json() or {}
        entries = data.get("entries", [])
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # naive: delete all and insert provided
        c.execute("DELETE FROM entries")
        for e in entries:
            c.execute(
                "INSERT INTO entries (date, start, end, description, is_absence) VALUES (?, ?, ?, ?, ?)",
                (e.get("date"), e.get("start"), e.get("end"), e.get("description"), 1 if e.get("is_absence") else 0),
            )
        conn.commit()
        conn.close()
        return jsonify({"saved": len(entries)})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@app.route("/api/load_entries")
def load_entries():
    if os.getenv("USE_SERVER_DB", "0") != "1":
        return jsonify({"error": "server persistence disabled"}), 403
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT date, start, end, description, is_absence FROM entries")
        rows = c.fetchall()
        conn.close()
        entries = []
        for r in rows:
            entries.append({
                "date": r[0],
                "start": r[1],
                "end": r[2],
                "description": r[3],
                "is_absence": bool(r[4]),
            })
        return jsonify({"entries": entries})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
