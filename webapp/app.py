from pathlib import Path
import os
import json
import hashlib
from datetime import timedelta
from flask import Flask, send_from_directory, request, jsonify, render_template, session
from appdirs import user_data_dir
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

APPNAME = "TimeTrackerWeb"
APPAUTHOR = "dennyschwender"

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Session configuration
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_NAME'] = 'timetracker_session'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Refresh session on each request


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
    
    # Check if old schema exists (entries table without user_id)
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entries'")
    entries_exists = c.fetchone() is not None
    
    if entries_exists:
        # Check if user_id column exists
        c.execute("PRAGMA table_info(entries)")
        columns = [row[1] for row in c.fetchall()]
        
        if 'user_id' not in columns:
            # Old schema detected - need to migrate
            print("Migrating database to new schema with user support...")
            
            # Rename old table
            c.execute("ALTER TABLE entries RENAME TO entries_old")
            
            # Create users table
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    pin_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            
            # Create new entries table with user_id
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT,
                    start TEXT,
                    end TEXT,
                    description TEXT,
                    is_absence INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
                """
            )
            
            # Create a default "legacy" user for old entries
            pin_hash = hash_pin("0000")  # default PIN
            c.execute("INSERT INTO users (username, pin_hash) VALUES (?, ?)", ("legacy", pin_hash))
            legacy_user_id = c.lastrowid
            
            # Migrate old entries to the new table
            c.execute("SELECT date, start, end, description, is_absence FROM entries_old")
            old_entries = c.fetchall()
            
            for entry in old_entries:
                c.execute(
                    "INSERT INTO entries (user_id, date, start, end, description, is_absence) VALUES (?, ?, ?, ?, ?, ?)",
                    (legacy_user_id, *entry)
                )
            
            # Drop old table
            c.execute("DROP TABLE entries_old")
            
            print(f"Migration complete! {len(old_entries)} entries moved to 'legacy' user (PIN: 0000)")
            
            conn.commit()
    else:
        # Fresh install - create tables
        # Users table with hashed PIN
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                pin_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Entries table with user_id foreign key
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT,
                start TEXT,
                end TEXT,
                description TEXT,
                is_absence INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )
        
        # Create index for faster lookups
        c.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_entries_user_id ON entries(user_id)
            """
        )
    
    conn.commit()
    conn.close()


def hash_pin(pin: str) -> str:
    """Hash a PIN using SHA-256"""
    return hashlib.sha256(pin.encode()).hexdigest()


def verify_pin(username: str, pin: str) -> tuple[bool, int]:
    """Verify username and PIN. Returns (success, user_id)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    pin_hash = hash_pin(pin)
    c.execute("SELECT id FROM users WHERE username = ? AND pin_hash = ?", (username, pin_hash))
    result = c.fetchone()
    conn.close()
    
    if result:
        return True, result[0]
    return False, None


def create_user(username: str, pin: str) -> tuple[bool, str, int]:
    """Create a new user. Returns (success, message, user_id)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        pin_hash = hash_pin(pin)
        c.execute("INSERT INTO users (username, pin_hash) VALUES (?, ?)", (username, pin_hash))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return True, "User created successfully", user_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists", None


# Initialize database on app startup
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ping")
def ping():
    return jsonify({
        "ok": True, 
        "authenticated": "user_id" in session,
        "server_db_enabled": os.getenv("USE_SERVER_DB", "0") == "1"
    })


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login with username and PIN"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    pin = data.get("pin", "").strip()
    
    if not username or not pin:
        return jsonify({"error": "Username and PIN required"}), 400
    
    success, user_id = verify_pin(username, pin)
    if success:
        session.clear()  # Clear any old session data first
        session.permanent = True  # Make session permanent (lasts 7 days)
        session["user_id"] = user_id
        session["username"] = username
        session.modified = True  # Explicitly mark session as modified
        return jsonify({"success": True, "username": username})
    else:
        return jsonify({"error": "Invalid username or PIN"}), 401


@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user with username and PIN"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    pin = data.get("pin", "").strip()
    
    if not username or not pin:
        return jsonify({"error": "Username and PIN required"}), 400
    
    if len(pin) < 4:
        return jsonify({"error": "PIN must be at least 4 digits"}), 400
    
    success, message, user_id = create_user(username, pin)
    if success:
        session.clear()  # Clear any old session data first
        session.permanent = True  # Make session permanent (lasts 7 days)
        session["user_id"] = user_id
        session["username"] = username
        session.modified = True  # Explicitly mark session as modified
        return jsonify({"success": True, "message": message, "username": username})
    else:
        return jsonify({"error": message}), 400


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Logout current user"""
    session.clear()
    return jsonify({"success": True})


@app.route("/api/auth/status")
def auth_status():
    """Check authentication status"""
    if "user_id" in session:
        return jsonify({"authenticated": True, "username": session.get("username")})
    return jsonify({"authenticated": False})


@app.route("/api/save_entries", methods=["POST"])
def save_entries():
    # optional server-side persistence; if disabled by env var, return 403
    if os.getenv("USE_SERVER_DB", "0") != "1":
        return jsonify({"error": "server persistence disabled"}), 403
    
    # Check authentication
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json() or {}
        entries = data.get("entries", [])
        user_id = session["user_id"]
        
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Delete only this user's entries
        c.execute("DELETE FROM entries WHERE user_id = ?", (user_id,))
        
        # Insert entries for this user
        for e in entries:
            c.execute(
                "INSERT INTO entries (user_id, date, start, end, description, is_absence) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, e.get("date"), e.get("start"), e.get("end"), e.get("description"), 1 if e.get("is_absence") else 0),
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
    
    # Check authentication
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session["user_id"]
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Load only this user's entries
        c.execute("SELECT date, start, end, description, is_absence FROM entries WHERE user_id = ?", (user_id,))
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
