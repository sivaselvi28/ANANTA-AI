"""
app.py - ANANTA | Main Streamlit Application
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Project modules
from database import create_sample_database
from schema_reader import get_schema, get_foreign_keys, get_row_counts
from history_manager import get_query_history, get_prompt_history, init_history_table
from agent import run_agent
from utils import df_to_csv_bytes, df_to_json_bytes, get_export_filename, weather_emoji

# ─────────────────────── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="ANANTA AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0F1117; color: #E0E0E0; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1A1F2E; border-right: 1px solid #2D3250; }
    
    /* Agent step cards */
    .step-card {
        background: #1A1F2E;
        border-left: 4px solid #4F8EF7;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 6px 0;
        font-family: monospace;
        font-size: 13px;
        white-space: pre-wrap;
    }
    .step-running { border-left-color: #F9C74F; }
    .step-success { border-left-color: #43D9A2; }
    .step-warning { border-left-color: #FF9F40; }
    .step-error   { border-left-color: #FF6B6B; }

    /* Metric cards */
    .metric-card {
        background: #1A1F2E;
        border: 1px solid #2D3250;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #4F8EF7; }
    .metric-label { font-size: 12px; color: #888; margin-top: 4px; }

    /* SQL block */
    .sql-block {
        background: #12151F;
        border: 1px solid #2D3250;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #43D9A2;
        overflow-x: auto;
    }

    /* Weather card */
    .weather-card {
        background: linear-gradient(135deg, #1e3a5f, #1A1F2E);
        border: 1px solid #2D5282;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    /* Section headers */
    .section-header {
        font-size: 16px;
        font-weight: 600;
        color: #CCCCFF;
        border-bottom: 1px solid #2D3250;
        padding-bottom: 6px;
        margin: 16px 0 10px 0;
    }

    /* Insight box */
    .insight-box {
        background: #16213E;
        border: 1px solid #3D5A80;
        border-radius: 10px;
        padding: 16px 20px;
        line-height: 1.7;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

.hero-wrap{padding:40px 20px 30px;background:linear-gradient(135deg,#0B1023,#111B4D,#013B3A);border-radius:24px;text-align:center;margin-bottom:25px;}
.hero-badge{display:inline-block;padding:10px 18px;border-radius:999px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);}
.hero-title{font-size:64px;font-weight:800;line-height:1.1;margin-top:20px;}
.hero-gradient{background:linear-gradient(90deg,#38bdf8,#8b5cf6);-webkit-background-clip:text;color:transparent;}
.hero-sub{font-size:20px;color:#b8c0d0;max-width:900px;margin:20px auto;}

</style>
""", unsafe_allow_html=True)

# ─────────────────────── Init ─────────────────────────────────────────────────
create_sample_database()
init_history_table()

# ─────────────────────── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 ANANTA AI")
    st.caption("Natural Language → SQL → Insights")
    st.divider()

    # Database Info
    st.markdown("### 🗄️ Database Info")
    try:
        schema = get_schema()
        counts = get_row_counts()
        fks = get_foreign_keys()

        for table, cols in schema.items():
            with st.expander(f"📊 {table} ({counts.get(table, 0)} rows)"):
                for col in cols:
                    icon = "🔑" if col["pk"] else "  "
                    st.markdown(
                        f"`{icon} {col['name']}` — *{col['type']}*"
                        + (" _(NN)_" if col["notnull"] else "")
                    )
        if fks:
            st.markdown("**Relationships:**")
            for t, fc, rt, rc in fks:
                st.caption(f"  {t}.{fc} → {rt}.{rc}")
    except Exception as e:
        st.error(f"Schema error: {e}")

    st.divider()

    # Prompt History
    st.markdown("### 📝 Prompt History")
    prompts = get_prompt_history(10)
    if prompts:
        for p in reversed(prompts[-5:]):
            ts = p[:21] if p.startswith("[") else ""
            q = p[22:] if ts else p
            st.caption(f"🕐 {ts}")
            st.markdown(f"> {q[:60]}{'...' if len(q) > 60 else ''}")
    else:
        st.caption("No prompts yet. Ask a question!")

    st.divider()

    # Query History
    st.markdown("### 🔍 Query History")
    history = get_query_history(5)
    if history:
        for h in history:
            icon = "✅" if h["success"] else "❌"
            st.caption(f"{icon} [{h['timestamp']}]")
            st.caption(f"   {h['question'][:50]}...")
    else:
        st.caption("No queries yet.")

    st.divider()

    # Agent Logs toggle
    st.markdown("### ⚙️ Settings")
    show_agent_steps = st.checkbox("Show Agent Thinking Steps", value=True)
    show_raw_sql = st.checkbox("Show Generated SQL", value=True)

# ─────────────────────── MAIN CONTENT ─────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
<div class="hero-badge">🟢 Powered by Ollama llama3 • runs locally</div>
<div class="hero-title">Talk to your database <span class="hero-gradient">like a human.</span></div>
<div class="hero-sub">A 7-step agent that turns plain English into safe SQL, live charts, and AI-written insights — no dashboards to wire, no queries to write.</div>
</div>
""", unsafe_allow_html=True)


# ── Quick Example Buttons ───────────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Quick Examples</div>', unsafe_allow_html=True)
ex_cols = st.columns(4)
examples = [
    "Show employees earning above 50000",
    "Which department has the highest average salary?",
    "List students from CSE with CGPA above 8",
    "Show total sales by product",
    "Compare sales across regions",
    "Show top 5 earners in the company",
    "What is the weather today in Mumbai?",
    "Show students sorted by CGPA descending",
]
selected_example = None
for i, ex in enumerate(examples):
    if ex_cols[i % 4].button(ex[:30] + ".." if len(ex) > 30 else ex, key=f"ex_{i}", use_container_width=True):
        selected_example = ex

# ── Question Input ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Ask Your Question</div>', unsafe_allow_html=True)

default_q = selected_example if selected_example else ""
if "last_question" not in st.session_state:
    st.session_state.last_question = ""

question = st.text_area(
    "Enter your question in natural language:",
    value=default_q,
    height=90,
    placeholder="e.g. Show employees earning above 50000, or What is today's weather in Delhi?",
    key="question_input",
)

col_run, col_clear = st.columns([1, 5])
run_btn = col_run.button("🚀 Analyze", type="primary", use_container_width=True)
if col_clear.button("🗑️ Clear", use_container_width=False):
    st.rerun()

# ─────────────────────── AGENT EXECUTION ──────────────────────────────────────
if run_btn and question.strip():
    st.session_state.last_question = question.strip()
    st.markdown("---")

    # Agent steps container
    if show_agent_steps:
        st.markdown('<div class="section-header">🧠 Agent Reasoning Steps</div>', unsafe_allow_html=True)
        steps_container = st.container()

    # Run agent loop
    final_result = None
    step_placeholders = {}

    with st.spinner("Agent is working..."):
        for result in run_agent(question.strip()):
            final_result = result

            if show_agent_steps:
                with steps_container:
                    for step in result.steps:
                        key = f"step_{step.step_num}"
                        if key not in step_placeholders:
                            step_placeholders[key] = st.empty()

                        status_icon = {
                            "running": "⏳", "success": "✅",
                            "warning": "⚠️", "error": "❌"
                        }.get(step.status, "🔵")

                        css_class = f"step-card step-{step.status}"
                        step_placeholders[key].markdown(
                            f'<div class="{css_class}">'
                            f'<b>Step {step.step_num}: {step.title}</b>  {status_icon}<br/>'
                            f'<span style="color:#aaa">{step.content}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

    # ── Results ─────────────────────────────────────────────────────────────
    if final_result and final_result.success:
        st.markdown("---")

        # Metrics row
        df = final_result.df
        st.markdown('<div class="section-header">📊 Query Results</div>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(df)}</div>'
            f'<div class="metric-label">Rows Returned</div></div>', unsafe_allow_html=True)
        m2.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(df.columns)}</div>'
            f'<div class="metric-label">Columns</div>', unsafe_allow_html=True)

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            avg_val = df[numeric_cols[0]].mean()
            m3.markdown(
                f'<div class="metric-card"><div class="metric-value">{avg_val:,.0f}</div>'
                f'<div class="metric-label">Avg {numeric_cols[0]}</div></div>', unsafe_allow_html=True)
            m4.markdown(
                f'<div class="metric-card"><div class="metric-value">{df[numeric_cols[0]].max():,.0f}</div>'
                f'<div class="metric-label">Max {numeric_cols[0]}</div></div>', unsafe_allow_html=True)
        else:
            m3.markdown(
                f'<div class="metric-card"><div class="metric-value">{len(df.columns)}</div>'
                f'<div class="metric-label">Columns</div></div>', unsafe_allow_html=True)
            m4.markdown(
                f'<div class="metric-card"><div class="metric-value">SELECT</div>'
                f'<div class="metric-label">Query Type</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Generated SQL
        if show_raw_sql and final_result.sql:
            st.markdown('<div class="section-header">💾 Generated SQL</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="sql-block">{final_result.sql}</div>',
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

        # Results table + Chart side by side
        col_table, col_chart = st.columns([1, 1])

        with col_table:
            st.markdown("**📋 Data Table**")
            st.dataframe(df, use_container_width=True, height=350)

            # Export buttons
            exp1, exp2 = st.columns(2)
            csv_bytes = df_to_csv_bytes(df)
            json_bytes = df_to_json_bytes(df)
            exp1.download_button(
                "⬇️ Export CSV", csv_bytes,
                file_name=get_export_filename(question, "csv"),
                mime="text/csv", use_container_width=True
            )
            exp2.download_button(
                "⬇️ Export JSON", json_bytes,
                file_name=get_export_filename(question, "json"),
                mime="application/json", use_container_width=True
            )

        with col_chart:
            if final_result.chart_bytes:
                st.markdown(f"**📈 {final_result.chart_desc}**")
                st.image(final_result.chart_bytes, use_container_width=True)
            else:
                st.info("📊 Chart not generated for this query shape.")

        # ── Insights ───────────────────────────────────────────────────────
        if final_result.insight:
            st.markdown("---")
            st.markdown('<div class="section-header">💡 AI Insights</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="insight-box">{final_result.insight}</div>',
                unsafe_allow_html=True
            )

        # ── External API Data ───────────────────────────────────────────────
        if final_result.api_data:
            st.markdown("---")
            if final_result.api_type == "weather":
                w = final_result.api_data
                emoji = weather_emoji(w.get("description", ""))
                st.markdown('<div class="section-header">🌐 Live Weather Data</div>', unsafe_allow_html=True)
                wc1, wc2, wc3, wc4 = st.columns(4)
                wc1.metric("📍 Location", f"{w['city']}, {w['country']}")
                wc2.metric(f"{emoji} Condition", w["description"])
                wc3.metric("🌡️ Temperature", f"{w['temperature']}°C", f"Feels {w['feels_like']}°C")
                wc4.metric("💧 Humidity", f"{w['humidity']}%")
                st.caption(f"Source: {w['source']} | Updated: {w['timestamp']}")

            elif final_result.api_type == "currency":
                r = final_result.api_data
                st.markdown('<div class="section-header">💱 Live Exchange Rates</div>', unsafe_allow_html=True)
                rates_df = pd.DataFrame(
                    [{"Currency": k, "Rate (per USD)": v} for k, v in r["rates"].items()]
                )
                st.dataframe(rates_df, use_container_width=True, hide_index=True)
                st.caption(f"Source: {r['source']} | Updated: {r['timestamp']}")

    elif final_result and not final_result.success:
        st.error(f"❌ Agent failed: {final_result.error}")

elif run_btn and not question.strip():
    st.warning("⚠️ Please enter a question first.")

# ─────────────────────── FOOTER ───────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>🤖 <b>ANANTA</b> | "
    "Powered by Ollama (llama3) + SQLite + Streamlit | "
    "Built for Hackathon 2024</small></center>",
    unsafe_allow_html=True,
)
