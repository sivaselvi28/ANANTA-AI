# 🤖 ANANTA AI

> **Ask questions in plain English. Get SQL queries, data tables, visualizations, and AI-powered insights — automatically.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20llama3-purple)](https://ollama.ai)
[![SQLite](https://img.shields.io/badge/Database-SQLite-green)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 What It Does

The ANANTA bridges the gap between natural language and database analytics. Type a question like *"Which department has the highest average salary?"* and the agent:

1. 🧠 Understands your intent
2. 📋 Reads the database schema automatically
3. ⚙️ Generates a valid SQL query via **Ollama llama3**
4. 🔒 Validates the query for safety (SELECT only)
5. 🚀 Executes it against SQLite
6. 🌐 Optionally enriches with live API data (weather / exchange rates)
7. 💡 Returns insights, charts, and recommendations

---

## ✨ Features

| Feature | Description |
|---|---|
| **Natural Language Querying** | Plain English → SQL via Ollama llama3 |
| **Agent Loop (7 Steps)** | Live step-by-step reasoning displayed in UI |
| **Schema Reader** | Auto-detects tables, columns, relationships |
| **Safety Layer** | Blocks DROP/DELETE/INSERT/UPDATE/ALTER/TRUNCATE |
| **External API** | Live weather (wttr.in) + exchange rates |
| **Insight Generator** | AI-written summaries, observations, recommendations |
| **Auto Visualization** | Bar / Pie / Line charts via Matplotlib |
| **Prompt History** | All prompts logged to `prompts.txt` |
| **Query History** | Questions + SQL + results stored in SQLite |
| **CSV/JSON Export** | One-click data download |
| **Fallback Mode** | Rule-based SQL when Ollama is offline |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-data-analyst-agent.git
cd ai-data-analyst-agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Ollama (AI Engine)
```bash
# Install Ollama from https://ollama.ai/download
# Then pull the llama3 model:
ollama pull llama3

# Start the Ollama server:
ollama serve
```

### 5. Run the App
```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 📁 Project Structure

```
ai-data-analyst-agent/
├── app.py               # Main Streamlit UI
├── agent.py             # 7-step agent reasoning loop
├── database.py          # SQLite setup + sample data creation
├── schema_reader.py     # Auto schema introspection
├── sql_generator.py     # Ollama llama3 NL→SQL generation
├── query_executor.py    # Safe SQL execution via pandas
├── safety_checker.py    # SQL validation (SELECT-only guard)
├── api_service.py       # Weather + exchange rate APIs
├── visualizer.py        # Auto chart generation (Matplotlib)
├── history_manager.py   # Prompt & query history storage
├── utils.py             # Export helpers and formatters
├── prompts.txt          # Auto-logged prompt history
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 💬 Example Questions

```
# Employee queries
"Show employees earning above 50000"
"Which department has the highest average salary?"
"List the top 5 highest paid employees"
"Show all employees in Engineering"

# Student queries
"List students from CSE department"
"Show students with CGPA above 8.5"
"Which city has the most students?"

# Sales queries
"Show total sales by product"
"Compare sales performance across regions"
"Which salesperson has the highest total sales?"
"Show monthly sales trend"

# Cross-table
"Show employees with their department names"

# API-enhanced
"Show employee data and today's weather in Mumbai"
"What are the current USD exchange rates?"
```

---

## 🗄️ Database Schema

The app auto-creates `database.db` with 4 tables and sample data:

**employees** — id, name, email, department_id, salary, hire_date, role  
**departments** — id, name, budget, location  
**students** — id, name, department, cgpa, year, email, city  
**sales** — id, product, amount, quantity, sale_date, region, salesperson  

---

## 🔒 Safety Architecture

All SQL goes through a strict safety filter before execution:

- ✅ **Allowed**: `SELECT` queries only
- ❌ **Blocked**: `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `TRUNCATE`, `CREATE`, `REPLACE`
- ❌ **Blocked**: SQL injection patterns (`--`, `/*`, `;--`)
- ❌ **Blocked**: Multiple statements separated by `;`

---

## 🌐 External API Integration

| API | Source | Key Required |
|---|---|---|
| Weather | wttr.in (fallback) | No |
| Weather | OpenWeatherMap | Optional |
| Exchange Rates | open.er-api.com | No |

Trigger by asking: *"...and today's weather in [city]"*

---

## 📊 Visualization Logic

Charts are auto-selected based on question keywords and data shape:

| Trigger Words | Chart Type |
|---|---|
| trend, over time, monthly, date | Line Chart |
| percent, distribution, breakdown | Pie Chart |
| compare, highest, average, salary | Bar Chart |
| (default, <10 unique values) | Bar Chart |
| (default, >10 unique values) | Line Chart |

---

## 📸 Screenshots

**Main Interface** — Dark-themed chat-style UI with quick example buttons  
**Agent Steps** — Live 7-step reasoning panel showing each decision  
**Results** — Data table + auto-generated chart side by side  
**Insights Panel** — AI-written analysis with summary, observations, and recommendations  
**Weather Widget** — Live weather data card integrated with query results  
**Sidebar** — Database schema browser, prompt history, query history

---

## 🔮 Future Enhancements

- [ ] Support for PostgreSQL / MySQL backends
- [ ] Multi-turn conversational memory
- [ ] CSV / JSON file upload to create new tables
- [ ] Voice input via Whisper API
- [ ] Scheduled reports via email
- [ ] Role-based access control
- [ ] Advanced chart types (heatmaps, scatter plots)
- [ ] LLM model selector (GPT-4, Claude, Gemini)
- [ ] Dashboard builder with pinned charts

---

## 📄 License

MIT License — free for personal and commercial use.

---

## 👤 Author

Built for Hackathon 2024 as an end-to-end AI data analytics system.  
Tech Stack: Python · Streamlit · SQLite · Ollama llama3 · Matplotlib

---

*⭐ If this project helped you, please give it a star on GitHub!*
