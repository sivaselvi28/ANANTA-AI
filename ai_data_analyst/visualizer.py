"""
visualizer.py - Auto-generates charts from query results using Matplotlib.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import numpy as np


CHART_COLORS = ["#4F8EF7", "#FF6B6B", "#43D9A2", "#F9C74F", "#9775FA", "#FF9F40", "#4BC0C0"]


def auto_visualize(df: pd.DataFrame, question: str = "") -> tuple[bytes | None, str]:
    """
    Automatically choose chart type and return (png_bytes, chart_description).
    Returns (None, reason) if visualization is not applicable.
    """
    if df is None or df.empty:
        return None, "No data to visualize."

    if len(df.columns) < 2:
        return None, "Need at least 2 columns for a chart."

    # Determine best chart type
    chart_type, x_col, y_col = _choose_chart(df, question)

    if chart_type == "none":
        return None, "Chart not applicable for this data shape."

    try:
        fig = _create_chart(df, chart_type, x_col, y_col, question)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="#0F1117")
        buf.seek(0)
        plt.close(fig)
        return buf.read(), f"{chart_type.title()} Chart: {y_col} by {x_col}"
    except Exception as e:
        plt.close("all")
        return None, f"Chart error: {str(e)}"


def _choose_chart(df: pd.DataFrame, question: str) -> tuple[str, str, str]:
    """Choose chart type based on data shape and question keywords."""
    q = question.lower()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()

    if not numeric_cols:
        return "none", "", ""

    y_col = numeric_cols[0]

    # Prefer a label/category column for x-axis
    if text_cols:
        x_col = text_cols[0]
    else:
        x_col = df.columns[0] if df.columns[0] != y_col else df.columns[1]

    # Choose chart type from keywords
    if any(kw in q for kw in ["trend", "over time", "monthly", "yearly", "date", "history"]):
        return "line", x_col, y_col
    if any(kw in q for kw in ["percent", "share", "distribution", "proportion", "breakdown"]):
        return "pie", x_col, y_col
    if any(kw in q for kw in ["compare", "highest", "lowest", "top", "rank", "average", "salary"]):
        return "bar", x_col, y_col

    # Default: bar for < 10 categories, line otherwise
    unique_x = df[x_col].nunique()
    if unique_x <= 10:
        return "bar", x_col, y_col
    return "line", x_col, y_col


def _create_chart(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str) -> plt.Figure:
    """Create styled Matplotlib figure."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#1A1F2E")

    # Limit rows for readability
    plot_df = df.head(15).copy()

    if chart_type == "bar":
        x_labels = plot_df[x_col].astype(str)
        y_vals = pd.to_numeric(plot_df[y_col], errors="coerce").fillna(0)
        bars = ax.bar(x_labels, y_vals, color=CHART_COLORS[:len(x_labels)], edgecolor="#0F1117", linewidth=0.5)
        ax.set_xlabel(x_col, color="#AAAAAA", fontsize=10)
        ax.set_ylabel(y_col, color="#AAAAAA", fontsize=10)
        plt.xticks(rotation=30, ha="right", color="#CCCCCC", fontsize=9)
        plt.yticks(color="#CCCCCC")
        # Value labels on bars
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                    f"{h:,.0f}", ha="center", va="bottom", color="#FFFFFF", fontsize=8)

    elif chart_type == "pie":
        x_labels = plot_df[x_col].astype(str)
        y_vals = pd.to_numeric(plot_df[y_col], errors="coerce").fillna(0)
        # Remove zeros
        mask = y_vals > 0
        y_vals, x_labels = y_vals[mask], x_labels[mask]
        wedges, texts, autotexts = ax.pie(
            y_vals, labels=None, autopct="%1.1f%%", colors=CHART_COLORS,
            startangle=140, pctdistance=0.82,
            wedgeprops={"linewidth": 0.5, "edgecolor": "#0F1117"},
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(9)
        legend_patches = [mpatches.Patch(color=CHART_COLORS[i % len(CHART_COLORS)], label=str(l))
                          for i, l in enumerate(x_labels)]
        ax.legend(handles=legend_patches, loc="lower right", fontsize=8,
                  facecolor="#1A1F2E", edgecolor="none", labelcolor="white")

    elif chart_type == "line":
        x_labels = plot_df[x_col].astype(str)
        y_vals = pd.to_numeric(plot_df[y_col], errors="coerce").fillna(0)
        ax.plot(x_labels, y_vals, color="#4F8EF7", linewidth=2.5, marker="o",
                markersize=6, markerfacecolor="#FF6B6B", markeredgewidth=0)
        ax.fill_between(range(len(x_labels)), y_vals, alpha=0.15, color="#4F8EF7")
        ax.set_xlabel(x_col, color="#AAAAAA", fontsize=10)
        ax.set_ylabel(y_col, color="#AAAAAA", fontsize=10)
        plt.xticks(range(len(x_labels)), x_labels, rotation=30, ha="right", color="#CCCCCC", fontsize=9)
        plt.yticks(color="#CCCCCC")
        ax.grid(True, alpha=0.1, color="#FFFFFF")

    # Common styling
    clean_title = title[:60] + "..." if len(title) > 60 else title
    ax.set_title(clean_title, color="#FFFFFF", fontsize=12, pad=14, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333344")

    plt.tight_layout()
    return fig
