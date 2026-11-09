import os
import sqlite3
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Local file of async results. Override with DB_URL in .env.
# Example: DB_URL=sqlite:///data/async_results.db
DEFAULT_DB_URL = "sqlite:///data/async_results.db"

# Column order matches SELECT * unpacking in scripts/utils.py.
CREATE_ASYNC_SUBMISSIONS = """
CREATE TABLE IF NOT EXISTS async_submissions.async_submissions (
    discord_id INTEGER,
    discord_name TEXT,
    async_time_timestamp TEXT,
    stream_key TEXT,
    initial_notif INTEGER,
    yt_live_notif INTEGER,
    streaming_notif INTEGER,
    seed_notif INTEGER,
    seed_number INTEGER
)
"""


def _db_path():
    """Turn DB_URL into a file path inside this project."""
    raw = os.getenv("DB_URL", DEFAULT_DB_URL).strip().strip("'\"")
    if raw.startswith("sqlite:///"):
        raw = raw[len("sqlite:///"):]
    if not os.path.isabs(raw):
        raw = os.path.join(BASE_DIR, raw)
    return os.path.normpath(raw)


def load_config(filename=None, section=None):
    """Return the SQLite file path. Kept so older imports still work."""
    return {"database": _db_path()}


def _open(config=None):
    """
    Open the async-results file.

    Existing SQL uses the name async_submissions.async_submissions
    (schema.table). SQLite has no schemas, so the file is attached
    under the name async_submissions. Opening the file itself shows
    a table named async_submissions.
    """
    db_path = (config or {}).get("database") or _db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(":memory:")
    conn.execute("ATTACH DATABASE ? AS async_submissions", (db_path,))
    conn.execute(CREATE_ASYNC_SUBMISSIONS)
    conn.commit()
    return conn


def _execute(conn, sql, params=None):
    """Run SQL. The rest of the bot still uses %s placeholders; SQLite wants ?."""
    cur = conn.cursor()
    adapted = sql.replace("%s", "?")
    if params:
        cur.execute(adapted, params)
    else:
        cur.execute(adapted)
    return cur


def connect(config=None):
    """Connect to the local SQLite database of async results."""
    try:
        conn = _open(config)
        print("Connected to the SQLite database.")
        return conn
    except (sqlite3.Error, Exception) as error:
        print(error)


def add_submission_to_db(discord_id, discord_name, async_time_timestamp, stream_key, initial_notif, yt_live_notif, streaming_notif, seed_notif, seed_number):
    """Insert one async submission and return its discord id."""
    sql = """INSERT INTO async_submissions.async_submissions(discord_id, discord_name, async_time_timestamp, stream_key, initial_notif, yt_live_notif, streaming_notif, seed_notif, seed_number)
             VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING discord_id, discord_name, seed_number;"""
    try:
        conn = _open()
        try:
            cur = _execute(conn, sql, (discord_id, discord_name, async_time_timestamp, stream_key, initial_notif, yt_live_notif, streaming_notif, seed_notif, seed_number))
            rows = cur.fetchone()
            if rows:
                some_sort_of_id = rows[0]
            conn.commit()
        finally:
            conn.close()
    except (Exception, sqlite3.Error) as error:
        print(error)


def query_database(sql, params=None):
    """Execute a SQL query on the local async-results database."""
    try:
        conn = _open()
        try:
            cur = _execute(conn, sql, params)
            conn.commit()
            if cur.description is None:
                return []
            return cur.fetchall()
        finally:
            conn.close()
    except (Exception, sqlite3.Error) as error:
        print(error)
        return None

def clear_async_submissions_table():
    """
    Completely clear all rows from the async_submissions.async_submissions table.
    """
    sql = "DELETE FROM async_submissions.async_submissions;"
    try:
        conn = _open()
        try:
            cur = _execute(conn, sql)
            conn.commit()
        finally:
            conn.close()
    except (Exception, sqlite3.Error) as error:
        print(error)


