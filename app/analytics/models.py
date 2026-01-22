"""
Analytics database models using SQLite
"""
import sqlite3
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "analytics.db"


def get_connection():
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Page views table (server-side, no cookies needed)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            path TEXT NOT NULL,
            ip_hash TEXT NOT NULL,
            user_agent TEXT,
            referrer TEXT,
            browser TEXT,
            device TEXT,
            os TEXT,
            country TEXT
        )
    """)

    # Sessions table (for extended tracking with consent)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            ip_hash TEXT NOT NULL,
            pages_visited INTEGER DEFAULT 1,
            consent_given INTEGER DEFAULT 0,
            user_agent TEXT
        )
    """)

    # Events table (clicks, scroll, etc. - only with consent)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_id TEXT,
            event_type TEXT NOT NULL,
            event_data TEXT,
            path TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    # Contact form submissions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS form_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            form_type TEXT NOT NULL,
            company TEXT,
            email TEXT,
            request_type TEXT,
            ip_hash TEXT
        )
    """)

    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_views_timestamp ON page_views(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_views_path ON page_views(path)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_views_ip_hash ON page_views(ip_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")

    conn.commit()
    conn.close()


def log_page_view(path: str, ip_hash: str, user_agent: str = None,
                  referrer: str = None, browser: str = None,
                  device: str = None, os: str = None, country: str = None):
    """Log a page view"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO page_views (timestamp, path, ip_hash, user_agent, referrer, browser, device, os, country)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), path, ip_hash, user_agent, referrer, browser, device, os, country))
    conn.commit()
    conn.close()


def create_session(session_id: str, ip_hash: str, user_agent: str = None, consent: bool = False):
    """Create a new session"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO sessions (id, started_at, ip_hash, user_agent, consent_given)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, datetime.utcnow().isoformat(), ip_hash, user_agent, 1 if consent else 0))
    conn.commit()
    conn.close()


def update_session(session_id: str, pages_visited: int = None, ended_at: str = None):
    """Update session data"""
    conn = get_connection()
    cursor = conn.cursor()

    updates = []
    values = []

    if pages_visited is not None:
        updates.append("pages_visited = ?")
        values.append(pages_visited)
    if ended_at is not None:
        updates.append("ended_at = ?")
        values.append(ended_at)

    if updates:
        values.append(session_id)
        cursor.execute(f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()

    conn.close()


def log_event(event_type: str, event_data: str = None, session_id: str = None, path: str = None):
    """Log an event (click, scroll, etc.)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (timestamp, session_id, event_type, event_data, path)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), session_id, event_type, event_data, path))
    conn.commit()
    conn.close()


def log_form_submission(form_type: str, company: str = None, email: str = None,
                        request_type: str = None, ip_hash: str = None):
    """Log a form submission"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO form_submissions (timestamp, form_type, company, email, request_type, ip_hash)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), form_type, company, email, request_type, ip_hash))
    conn.commit()
    conn.close()


# Initialize database on import
init_db()
