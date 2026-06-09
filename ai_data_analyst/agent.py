"""
agent.py - The AI Agent Loop: 7-step reasoning workflow for answering data questions.
"""
import pandas as pd
from datetime import datetime
from typing import Generator

from schema_reader import get_schema_text, get_schema
from sql_generator import generate_sql, generate_insight, check_ollama_connection
from safety_checker import is_safe_sql, sanitize_sql
from query_executor import execute_query, summarize_results
from api_service import detect_api_intent, get_weather, get_exchange_rates
from history_manager import save_prompt, save_query_history
from visualizer import auto_visualize


class AgentStep:
    def __init__(self, step_num: int, title: str, status: str = "running", content: str = ""):
        self.step_num = step_num
        self.title = title
        self.status = status  # running | success | warning | error
        self.content = content
        self.timestamp = datetime.now().strftime("%H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "step": self.step_num,
            "title": self.title,
            "status": self.status,
            "content": self.content,
            "timestamp": self.timestamp,
        }


class AgentResult:
    def __init__(self):
        self.steps: list[AgentStep] = []
        self.sql: str = ""
        self.df: pd.DataFrame | None = None
        self.insight: str = ""
        self.chart_bytes: bytes | None = None
        self.chart_desc: str = ""
        self.api_data: dict | None = None
        self.api_type: str = ""
        self.error: str = ""
        self.success: bool = False


def run_agent(question: str) -> Generator[AgentResult, None, None]:
    """
    Main agent loop - 7 steps with real-time yield for UI updates.
    Yields AgentResult after each step so Streamlit can show live progress.
    """
    result = AgentResult()

    # ── Step 1: Understand Question ───────────────────────────────────────────
    step1 = AgentStep(1, "🧠 Understanding Your Question")
    result.steps.append(step1)
    yield result

    # Save prompt
    save_prompt(question)

    # Check Ollama
    ollama_ok = check_ollama_connection()
    if not ollama_ok:
        step1.status = "warning"
        step1.content = (
            "⚠️ Ollama is not running. Using rule-based SQL fallback.\n"
            "To enable AI: run `ollama serve` then `ollama pull llama3`"
        )
    else:
        step1.status = "success"
        step1.content = f"Question received: \"{question}\"\nOllama (llama3) is connected ✓"
    yield result

    # Detect API intent
    api_type, api_param = detect_api_intent(question)

    # ── Step 2: Read Schema ────────────────────────────────────────────────────
    step2 = AgentStep(2, "📋 Reading Database Schema")
    result.steps.append(step2)
    yield result

    try:
        schema_text = get_schema_text()
        schema_dict = get_schema()
        table_names = list(schema_dict.keys())
        step2.status = "success"
        step2.content = f"Found {len(table_names)} tables: {', '.join(table_names)}\n\nSchema:\n{schema_text}"
    except Exception as e:
        step2.status = "error"
        step2.content = f"Failed to read schema: {e}"
        result.error = str(e)
        yield result
        return

    yield result

    # ── Step 3: Generate SQL ───────────────────────────────────────────────────
    step3 = AgentStep(3, "⚙️ Generating SQL Query")
    result.steps.append(step3)
    yield result

    if ollama_ok:
        raw_sql, raw_response = generate_sql(question, schema_text)
        sql = sanitize_sql(raw_sql)
    else:
        sql, raw_response = _fallback_sql(question, schema_dict)

    if not sql:
        step3.status = "error"
        step3.content = f"SQL generation failed.\nOllama response: {raw_response}"
        result.error = "Could not generate SQL."
        yield result
        return

    result.sql = sql
    step3.status = "success"
    step3.content = f"Generated SQL:\n```sql\n{sql}\n```"
    yield result

    # ── Step 4: Validate SQL ───────────────────────────────────────────────────
    step4 = AgentStep(4, "🔒 Validating SQL (Safety Check)")
    result.steps.append(step4)
    yield result

    is_safe, reason = is_safe_sql(sql)
    if not is_safe:
        step4.status = "error"
        step4.content = f"⛔ BLOCKED: {reason}"
        result.error = reason
        save_query_history(question, sql, 0, False, reason)
        yield result
        return

    step4.status = "success"
    step4.content = f"✅ Safety check passed: {reason}\nOnly SELECT statements allowed — confirmed."
    yield result

    # ── Step 5: Execute Query ──────────────────────────────────────────────────
    step5 = AgentStep(5, "🚀 Executing Query")
    result.steps.append(step5)
    yield result

    df, error = execute_query(sql)
    if error or df is None:
        step5.status = "error"
        step5.content = f"Execution failed:\n{error}"
        result.error = error
        save_query_history(question, sql, 0, False, error)
        yield result
        return

    result.df = df
    step5.status = "success"
    step5.content = f"Query executed successfully.\nReturned {len(df)} rows × {len(df.columns)} columns."
    save_query_history(question, sql, len(df), True)
    yield result

    # ── Step 6: External API ───────────────────────────────────────────────────
    step6 = AgentStep(6, "🌐 Fetching External API Data")
    result.steps.append(step6)
    yield result

    if api_type == "weather":
        weather = get_weather(api_param)
        result.api_data = weather
        result.api_type = "weather"
        step6.status = "success"
        step6.content = (
            f"Weather data fetched for {weather['city']}:\n"
            f"  Temperature: {weather['temperature']}°C\n"
            f"  Condition: {weather['description']}\n"
            f"  Humidity: {weather['humidity']}%\n"
            f"  Source: {weather['source']}"
        )
    elif api_type == "currency":
        rates = get_exchange_rates()
        result.api_data = rates
        result.api_type = "currency"
        step6.status = "success"
        rate_lines = "\n".join(f"  {k}: {v}" for k, v in rates["rates"].items())
        step6.content = f"Exchange rates fetched (Base: {rates['base']}):\n{rate_lines}"
    else:
        step6.status = "success"
        step6.content = "No external API data needed for this query."
    yield result

    # ── Step 7: Analyze & Insight ──────────────────────────────────────────────
    step7 = AgentStep(7, "💡 Generating Insights & Visualization")
    result.steps.append(step7)
    yield result

    # Generate insight
    results_summary = summarize_results(df)
    if ollama_ok and not df.empty:
        insight = generate_insight(question, sql, results_summary, schema_text)
    else:
        insight = _basic_insight(df, question)
    result.insight = insight

    # Generate chart
    chart_bytes, chart_desc = auto_visualize(df, question)
    result.chart_bytes = chart_bytes
    result.chart_desc = chart_desc

    step7.status = "success"
    step7.content = (
        f"Insights generated ✓\n"
        f"Chart: {chart_desc}\n"
        f"Result rows: {len(df)}"
    )
    result.success = True
    yield result


def _fallback_sql(question: str, schema: dict) -> tuple[str, str]:
    """Simple rule-based SQL when Ollama is unavailable."""
    q = question.lower()
    tables = list(schema.keys())

    # Detect target table
    target = tables[0]
    for t in tables:
        if t in q:
            target = t
            break

    # Build simple query
    cols = [c["name"] for c in schema.get(target, [])]
    col_str = ", ".join(cols) if cols else "*"

    # Salary filter
    if "above" in q or "greater" in q or "more than" in q:
        for col in cols:
            if "salary" in col or "amount" in col:
                sql = f"SELECT * FROM {target} WHERE {col} > 50000 LIMIT 50"
                return sql, sql

    # Average
    if "average" in q or "avg" in q:
        for col in cols:
            if any(x in col for x in ["salary", "amount", "cgpa", "price"]):
                sql = f"SELECT AVG({col}) as average_{col} FROM {target}"
                return sql, sql

    # Count
    if "count" in q or "how many" in q:
        sql = f"SELECT COUNT(*) as total FROM {target}"
        return sql, sql

    # Default: show all
    sql = f"SELECT * FROM {target} LIMIT 50"
    return sql, sql


def _basic_insight(df: pd.DataFrame, question: str) -> str:
    """Generate basic insight without Ollama."""
    if df is None or df.empty:
        return "No results found for this query."

    lines = [f"**Summary**: Found {len(df)} records matching your query."]

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        col = numeric_cols[0]
        lines.append(f"\n**Key Observations**:")
        lines.append(f"- {col}: Min = {df[col].min():,.2f}, Max = {df[col].max():,.2f}, Avg = {df[col].mean():,.2f}")
        if len(numeric_cols) > 1:
            col2 = numeric_cols[1]
            lines.append(f"- {col2}: Total = {df[col2].sum():,.2f}")

    lines.append(f"\n**Recommendation**: Review the {len(df)} records above for actionable patterns.")
    return "\n".join(lines)
