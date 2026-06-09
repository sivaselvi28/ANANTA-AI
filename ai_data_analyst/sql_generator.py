"""
sql_generator.py - Generates SQL queries from natural language using Ollama (llama3).
"""
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def generate_sql(question: str, schema_text: str) -> tuple[str, str]:
    """
    Returns (sql_query, raw_response).
    Calls Ollama llama3 to convert NL question → SQL.
    """
    prompt = f"""You are an expert SQLite SQL query generator.

Database Schema:
{schema_text}

Rules:
- Generate ONLY a single valid SQLite SELECT query.
- Do NOT include explanations, markdown fences, or comments.
- Output only the raw SQL query starting with SELECT.
- Use exact table and column names from the schema.
- Use proper SQLite syntax (no TOP, use LIMIT instead).
- For string comparisons use LIKE or = as appropriate.

User Question: {question}

SQL Query:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        raw = data.get("response", "").strip()
        return raw, raw
    except requests.exceptions.ConnectionError:
        return "", "❌ Cannot connect to Ollama. Make sure it's running: `ollama serve`"
    except Exception as e:
        return "", f"❌ Ollama error: {str(e)}"


def generate_insight(question: str, sql: str, results_summary: str, schema_text: str) -> str:
    """Generate a natural-language insight report from query results."""
    prompt = f"""You are a senior data analyst. Analyze the following query result and provide insights.

User Question: {question}
SQL Query: {sql}
Query Results Summary: {results_summary}

Provide a structured analysis with:
1. **Summary**: A 2-3 sentence summary of what was found.
2. **Key Observations**: 2-4 bullet points highlighting important findings.
3. **Recommendations**: 1-2 actionable recommendations based on the data.

Keep it concise, professional, and data-driven. Use numbers from the results."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"Insight generation unavailable: {str(e)}"


def check_ollama_connection() -> bool:
    """Check if Ollama is running."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False
