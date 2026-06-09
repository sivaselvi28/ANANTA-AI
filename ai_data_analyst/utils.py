"""
utils.py - Utility helpers for export, formatting, and display.
"""
import pandas as pd
import json
import io
from datetime import datetime


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode("utf-8")


def df_to_json_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to JSON bytes for download."""
    return df.to_json(orient="records", indent=2).encode("utf-8")


def get_export_filename(question: str, ext: str) -> str:
    """Generate a clean filename based on the question."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = question[:30].lower().replace(" ", "_").replace("?", "").replace("/", "_")
    return f"query_{slug}_{timestamp}.{ext}"


def format_number(n: float) -> str:
    """Format numbers cleanly."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n:,.0f}"
    return f"{n:.2f}"


def truncate_text(text: str, max_len: int = 80) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text


def weather_emoji(description: str) -> str:
    """Return emoji for weather description."""
    d = description.lower()
    if "rain" in d: return "🌧️"
    if "cloud" in d: return "☁️"
    if "sun" in d or "clear" in d: return "☀️"
    if "snow" in d: return "❄️"
    if "storm" in d or "thunder" in d: return "⛈️"
    if "mist" in d or "fog" in d: return "🌫️"
    return "🌡️"
