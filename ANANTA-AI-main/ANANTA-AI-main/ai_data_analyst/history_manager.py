"""
history_manager.py - Stores prompt history in prompts.txt and query history in SQLite.
"""
import sqlite3
import json
from datetime import datetime
from database import get_connection

PROMPTS_FILE = "prompts.txt"


def init_history_table():
    """Create query_history table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            sql_query TEXT,
            row_count INTEGER,
            timestamp TEXT,
            success INTEGER,
            error_msg TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_prompt(question: str):
    """Append prompt to prompts.txt (satisfies prompt documentation requirement)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PROMPTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {question}\n")


def save_query_history(question: str, sql: str, row_count: int, success: bool, error_msg: str = ""):
    """Save query execution record to SQLite."""
    try:
        init_history_table()
        conn = get_connection()
        conn.execute("""
            INSERT INTO query_history (question, sql_query, row_count, timestamp, success, error_msg)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (question, sql, row_count, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              int(success), error_msg))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"History save error: {e}")


def get_query_history(limit: int = 20) -> list:
    """Return recent query history records."""
    try:
        init_history_table()
        conn = get_connection()
        cursor = conn.execute("""
            SELECT id, question, sql_query, row_count, timestamp, success, error_msg
            FROM query_history ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0], "question": r[1], "sql": r[2],
                "rows": r[3], "timestamp": r[4],
                "success": bool(r[5]), "error": r[6],
            }
            for r in rows
        ]
    except Exception:
        return []


def get_prompt_history(limit: int = 20) -> list:
    """Return last N lines from prompts.txt."""
    try:
        with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [l.strip() for l in lines[-limit:] if l.strip()]
    except FileNotFoundError:
        return []
