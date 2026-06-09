"""
query_executor.py - Executes validated SQL queries
against the SQLite database.
"""

import sqlite3
import pandas as pd
from database import get_connection
from safety_checker import is_safe_sql


def execute_query(sql: str) -> tuple[pd.DataFrame | None, str]:
    """
    Execute only safe SELECT queries.
    Returns (DataFrame, error_message).
    """

    # Safety validation
    safe, message = is_safe_sql(sql)

    if not safe:
        return None, message

    try:
        conn = get_connection()

        # Execute SELECT query
        df = pd.read_sql_query(sql, conn)

        conn.close()

        return df, ""

    except sqlite3.OperationalError as e:
        return None, f"SQL Error: {str(e)}"

    except Exception as e:
        return None, f"Execution Error: {str(e)}"


def summarize_results(
    df: pd.DataFrame,
    max_rows: int = 10
) -> str:
    """
    Convert DataFrame to a text summary.
    """

    if df is None or df.empty:
        return "No results found."

    rows = df.head(max_rows).to_dict(
        orient="records"
    )

    summary_lines = [
        f"Total rows: {len(df)}",
        "Sample data:"
    ]

    for i, row in enumerate(rows, 1):
        summary_lines.append(
            f"  Row {i}: {row}"
        )

    numeric_cols = (
        df.select_dtypes(include="number")
        .columns.tolist()
    )

    if numeric_cols:
        summary_lines.append("Numeric stats:")

        for col in numeric_cols[:4]:
            summary_lines.append(
                f"  {col}: "
                f"min={df[col].min():.2f}, "
                f"max={df[col].max():.2f}, "
                f"avg={df[col].mean():.2f}"
            )

    return "\n".join(summary_lines)