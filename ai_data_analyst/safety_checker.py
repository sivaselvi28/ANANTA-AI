"""
safety_checker.py - Validates SQL queries to allow only SELECT statements.
"""
import re

BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER",
    "TRUNCATE", "CREATE", "REPLACE", "ATTACH", "DETACH",
    "PRAGMA", "--", ";--", "/*", "*/"
]


def is_safe_sql(sql: str) -> tuple[bool, str]:
    """
    Returns (is_safe, reason).
    Allows only SELECT queries; blocks everything else.
    """
    if not sql or not sql.strip():
        return False, "Empty SQL query."

    cleaned = sql.strip().upper()

    # Must start with SELECT
    if not cleaned.startswith("SELECT"):
        return False, f"Only SELECT statements are allowed. Your query starts with a different command."

    # Check for blocked keywords
    for kw in BLOCKED_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, cleaned):
            return False, f"Blocked keyword detected: '{kw}'. Only read-only SELECT queries are permitted."

    # Block multiple statements
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    if len(statements) > 1:
        return False, "Multiple SQL statements are not allowed. Please send one SELECT query at a time."

    return True, "SQL is safe."


def sanitize_sql(sql: str) -> str:
    """Strip code fences and extra whitespace from LLM-generated SQL."""
    sql = re.sub(r"```sql|```", "", sql, flags=re.IGNORECASE)
    sql = sql.strip().rstrip(";")
    return sql
