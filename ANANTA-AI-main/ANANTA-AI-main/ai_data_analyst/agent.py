"""
agent.py - The AI Agent Loop: 7-step reasoning workflow for answering data questions.
"""

import pandas as pd
from datetime import datetime
from typing import Generator

from schema_reader import get_schema_text, get_schema
from sql_generator import (
    generate_sql,
    generate_insight,
    check_ollama_connection,
)
from safety_checker import (
    is_safe_sql,
    sanitize_sql,
)
from query_executor import (
    execute_query,
    summarize_results,
)
from api_service import (
    detect_api_intent,
    get_weather,
    get_exchange_rates,
)
from history_manager import (
    save_prompt,
    save_query_history,
)
from visualizer import auto_visualize


class AgentStep:
    def __init__(
        self,
        step_num: int,
        title: str,
        status: str = "running",
        content: str = "",
    ):
        self.step_num = step_num
        self.title = title
        self.status = status
        self.content = content
        self.timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

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


def run_agent(
    question: str,
) -> Generator[AgentResult, None, None]:

    result = AgentResult()

    # ── Step 1: Understand Question ──
    step1 = AgentStep(
        1,
        "🧠 Understanding Your Question"
    )

    result.steps.append(step1)
    yield result

    # Save prompt
    save_prompt(question)

    # ── EARLY SAFETY CHECK ──
    dangerous_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "rename",
        "replace",
        "grant",
        "revoke",
        "attach",
        "detach",
        "pragma",
    ]

    question_lower = question.lower()

    for keyword in dangerous_keywords:
        if keyword in question_lower:

            step1.status = "error"
            step1.content = (
                f"⛔ Dangerous operation "
                f"detected: "
                f"{keyword.upper()}\n\n"
                f"Read-only mode enabled.\n"
                f"Only SELECT queries "
                f"are allowed."
            )

            result.error = (
                f"Dangerous operation "
                f"detected: "
                f"{keyword.upper()}"
            )

            yield result
            return

    # Check Ollama
    ollama_ok = check_ollama_connection()

    if not ollama_ok:
        step1.status = "warning"

        step1.content = (
            "⚠️ Ollama is not running.\n"
            "Using rule-based SQL fallback.\n\n"
            "To enable AI:\n"
            "`ollama serve`\n"
            "`ollama pull llama3`"
        )

    else:
        step1.status = "success"

        step1.content = (
            f'Question received: '
            f'"{question}"\n'
            f"Ollama (llama3) "
            f"is connected ✓"
        )

    yield result

    # Detect API intent
    api_type, api_param = (
        detect_api_intent(question)
    )

    # ── Step 2: Read Schema ──
    step2 = AgentStep(
        2,
        "📋 Reading Database Schema"
    )

    result.steps.append(step2)
    yield result

    try:
        schema_text = get_schema_text()
        schema_dict = get_schema()

        table_names = list(
            schema_dict.keys()
        )

        step2.status = "success"

        step2.content = (
            f"Found "
            f"{len(table_names)} tables:\n"
            f"{', '.join(table_names)}"
            f"\n\nSchema:\n"
            f"{schema_text}"
        )

    except Exception as e:
        step2.status = "error"
        step2.content = (
            f"Failed to read schema: {e}"
        )

        result.error = str(e)

        yield result
        return

    yield result

    # ── Step 3: Generate SQL ──
    step3 = AgentStep(
        3,
        "⚙️ Generating SQL Query"
    )

    result.steps.append(step3)
    yield result

    if ollama_ok:
        raw_sql, raw_response = (
            generate_sql(
                question,
                schema_text
            )
        )

        sql = sanitize_sql(raw_sql)

    else:
        sql, raw_response = (
            _fallback_sql(
                question,
                schema_dict
            )
        )

    if not sql:
        step3.status = "error"

        step3.content = (
            "SQL generation failed.\n"
            f"Ollama response:\n"
            f"{raw_response}"
        )

        result.error = (
            "Could not generate SQL."
        )

        yield result
        return

    result.sql = sql

    step3.status = "success"

    step3.content = (
        f"Generated SQL:\n"
        f"```sql\n{sql}\n```"
    )

    yield result

    # ── Step 4: Validate SQL ──
    step4 = AgentStep(
        4,
        "🔒 Validating SQL "
        "(Safety Check)"
    )

    result.steps.append(step4)
    yield result

    is_safe, reason = (
        is_safe_sql(sql)
    )

    if not is_safe:
        step4.status = "error"

        step4.content = (
            f"⛔ BLOCKED:\n{reason}"
        )

        result.error = reason

        save_query_history(
            question,
            sql,
            0,
            False,
            reason,
        )

        yield result
        return

    step4.status = "success"

    step4.content = (
        f"✅ Safety check passed:\n"
        f"{reason}\n\n"
        f"Only SELECT "
        f"statements allowed."
    )

    yield result

    # ── Step 5: Execute Query ──
    step5 = AgentStep(
        5,
        "🚀 Executing Query"
    )

    result.steps.append(step5)
    yield result

    df, error = execute_query(sql)

    if error or df is None:
        step5.status = "error"

        step5.content = (
            f"Execution failed:\n"
            f"{error}"
        )

        result.error = error

        save_query_history(
            question,
            sql,
            0,
            False,
            error,
        )

        yield result
        return

    result.df = df

    step5.status = "success"

    step5.content = (
        f"Query executed "
        f"successfully.\n"
        f"Returned "
        f"{len(df)} rows × "
        f"{len(df.columns)} columns."
    )

    save_query_history(
        question,
        sql,
        len(df),
        True,
    )

    yield result

    # ── Step 7: Insights ──
    step7 = AgentStep(
        7,
        "💡 Generating Insights "
        "& Visualization"
    )

    result.steps.append(step7)
    yield result

    results_summary = (
        summarize_results(df)
    )

    if ollama_ok and not df.empty:
        insight = generate_insight(
            question,
            sql,
            results_summary,
            schema_text,
        )
    else:
        insight = _basic_insight(
            df,
            question,
        )

    result.insight = insight

    chart_bytes, chart_desc = (
        auto_visualize(
            df,
            question,
        )
    )

    result.chart_bytes = chart_bytes
    result.chart_desc = chart_desc

    step7.status = "success"

    step7.content = (
        "Insights generated ✓\n"
        f"Chart: {chart_desc}\n"
        f"Result rows: {len(df)}"
    )

    result.success = True
    yield result