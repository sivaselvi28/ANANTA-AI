"""
query_executor.py - Executes validated SQL queries against the SQLite database.
"""
import sqlite3
import pandas as pd
from database import get_connection


def execute_query(sql: str) -> tuple[pd.DataFrame | None, str]:
    """
    Execute a SQL SELECT query and return (DataFrame, error_message).
    Returns (None, error_msg) on failure.
    """
    try:
        conn = get_connection()
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df, ""
    except sqlite3.OperationalError as e:
        return None, f"SQL Error: {str(e)}"
    except Exception as e:
        return None, f"Execution Error: {str(e)}"


def summarize_results(df: pd.DataFrame, max_rows: int = 10) -> str:
    """Convert DataFrame to a text summary for the LLM."""
    if df is None or df.empty:
        return "No results found."

    rows = df.head(max_rows).to_dict(orient="records")
    summary_lines = [f"Total rows: {len(df)}", "Sample data:"]
    for i, row in enumerate(rows, 1):
        summary_lines.append(f"  Row {i}: {row}")

    # Add numeric stats if applicable
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        summary_lines.append("Numeric stats:")
        for col in numeric_cols[:4]:  # limit to 4 columns
            summary_lines.append(
                f"  {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, avg={df[col].mean():.2f}"
            )

    return "\n".join(summary_lines)
