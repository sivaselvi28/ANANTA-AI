# NL → SQL Query Builder for SQLite

## Overview

NL → SQL Query Builder for SQLite is an AI-powered application that enables users to interact with a SQLite database using natural language. Instead of writing SQL queries manually, users can ask questions in plain English, and the system automatically generates SQL, executes it safely, and displays the results along with an explanation.

The project is designed to make database querying accessible to non-technical users while ensuring security and transparency.

---

## Problem Statement

Many users find it difficult to write SQL queries, especially when dealing with:

* Table joins
* Filtering conditions
* Aggregations
* Grouping and sorting
* Complex database structures

This project removes the need for SQL knowledge by allowing users to query databases using natural language.

---

## Solution

The application accepts a user's natural language question, analyzes the SQLite database schema, generates the corresponding SQL query using a Large Language Model, validates the query for safety, executes it, and displays the results.

### Example

**User Input**

```text
Show the top 5 customers with the highest purchase amount
```

**Generated SQL**

```sql
SELECT c.name,
       SUM(o.amount) AS total_purchase
FROM Customers c
JOIN Orders o
ON c.customer_id = o.customer_id
GROUP BY c.customer_id
ORDER BY total_purchase DESC
LIMIT 5;
```

---

## Features

* Natural Language to SQL conversion
* Automatic database schema detection
* SQL query generation using AI
* Read-only query execution
* SQL query explanation
* Results displayed in tabular format
* Safety validation for generated SQL
* User-friendly Streamlit interface
* Error handling and query feedback

---

## Technology Stack

| Component       | Technology   |
| --------------- | ------------ |
| Frontend        | Streamlit    |
| Backend         | Python       |
| Database        | SQLite       |
| AI Model        | GPT / Claude |
| Data Processing | Pandas       |
| Database Access | sqlite3      |

---

## System Architecture

```text
User
 │
 ▼
Streamlit Interface
 │
 ▼
Natural Language Query
 │
 ▼
Schema Extraction
 │
 ▼
LLM (GPT / Claude)
 │
 ▼
SQL Generation
 │
 ▼
Safety Validation
 │
 ▼
SQLite Database
 │
 ▼
Results + SQL + Explanation
```

---

## Workflow

### Step 1: User Input

The user enters a question in plain English.

Example:

```text
Show employees with salary greater than 50000
```

---

### Step 2: Schema Extraction

The system retrieves:

* Table names
* Column names
* Relationships

from the SQLite database.

---

### Step 3: SQL Generation

The database schema and user query are sent to the LLM.

The model generates a valid SQLite query.

---

### Step 4: Safety Validation

The system validates the generated SQL before execution.

Blocked operations:

```sql
DROP
DELETE
UPDATE
INSERT
ALTER
TRUNCATE
```

Only SELECT queries are allowed.

---

### Step 5: Query Execution

The validated SQL query is executed using SQLite.

---

### Step 6: Results Display

The application displays:

* Generated SQL
* Query Results
* Query Explanation

---

## Project Structure

```text
NL-SQL-Builder/
│
├── app.py
├── database/
│   └── sample.db
│
├── utils/
│   ├── schema_reader.py
│   ├── sql_generator.py
│   ├── validator.py
│   └── executor.py
│
├── requirements.txt
├── README.md
└── .env
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/nl-sql-builder.git
cd nl-sql-builder
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

```bash
streamlit run app.py
```

Open your browser and navigate to:

```text
http://localhost:8501
```

---

## Example Usage

### Input

```text
Show all customers from Chennai
```

### Generated SQL

```sql
SELECT *
FROM Customers
WHERE city = 'Chennai';
```

### Output

| Customer ID | Name  | City    |
| ----------- | ----- | ------- |
| 101         | Ravi  | Chennai |
| 102         | Priya | Chennai |

### Explanation

The query retrieves all customers whose city is Chennai from the Customers table.

---

## Safety Mechanism

To prevent accidental or malicious database modifications:

* Only SELECT statements are executed.
* Destructive SQL commands are blocked.
* Validation occurs before query execution.
* Unsafe queries are rejected with an error message.

---

## Future Enhancements

* Support for MySQL and PostgreSQL
* Query history
* Data visualization charts
* Export results to CSV and Excel
* User authentication
* Conversational chat interface
* Multi-database support
* RAG-based schema retrieval for larger databases

---

## Challenges Faced

* Accurate SQL generation
* Handling complex joins
* Preventing unsafe queries
* Schema grounding for better AI performance
* Error handling for invalid SQL

---

## Impact

This project enables users without SQL knowledge to retrieve meaningful information from databases quickly and efficiently. It improves accessibility, productivity, and user experience while maintaining database security.

---

## Team

**Project Name:** NL → SQL Query Builder for SQLite

**Category:** AI + Database Automation

**Developed For:** Hackathon / Academic Project

---

## Conclusion

NL → SQL Query Builder for SQLite bridges the gap between natural language and databases. By combining AI, SQLite, and Streamlit, the system allows anyone to query data using simple English while ensuring safety, transparency, and ease of use.
