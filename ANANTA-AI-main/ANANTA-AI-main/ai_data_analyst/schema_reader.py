"""
schema_reader.py - Reads and formats the SQLite database schema.
"""
import sqlite3
from database import get_connection


def get_schema() -> dict:
    """Return full schema as a dict: {table: [columns]}"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        schema[table] = [
            {
                "cid": c[0],
                "name": c[1],
                "type": c[2],
                "notnull": bool(c[3]),
                "pk": bool(c[5]),
            }
            for c in cols
        ]
    conn.close()
    return schema


def get_schema_text() -> str:
    """Return schema formatted as SQL CREATE-like text for the LLM prompt."""
    schema = get_schema()
    lines = []
    for table, cols in schema.items():
        col_defs = ", ".join(
            f"{c['name']} {c['type']}{'  PK' if c['pk'] else ''}"
            for c in cols
        )
        lines.append(f"Table: {table}  ({col_defs})")
    return "\n".join(lines)


def get_foreign_keys() -> list:
    """Return list of (table, from_col, ref_table, ref_col) tuples."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    fks = []
    for table in tables:
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        for row in cursor.fetchall():
            fks.append((table, row[3], row[2], row[4]))
    conn.close()
    return fks


def get_row_counts() -> dict:
    """Return {table: row_count} dict."""
    conn = get_connection()
    cursor = conn.cursor()
    schema = get_schema()
    counts = {}
    for table in schema:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    conn.close()
    return counts
