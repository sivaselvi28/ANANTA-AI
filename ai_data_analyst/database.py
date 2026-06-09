"""
database.py - Creates and manages the SQLite database with sample data.
"""
import sqlite3
import os

DB_PATH = "database.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_sample_database():
    """Create database with sample tables and records if it doesn't exist."""
    if os.path.exists(DB_PATH):
        return
    conn = get_connection()
    cursor = conn.cursor()

    # Departments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        budget REAL,
        location TEXT
    )""")

    # Employees
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        department_id INTEGER,
        salary REAL,
        hire_date TEXT,
        role TEXT,
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )""")

    # Students
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT,
        cgpa REAL,
        year INTEGER,
        email TEXT,
        city TEXT
    )""")

    # Sales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT NOT NULL,
        amount REAL,
        quantity INTEGER,
        sale_date TEXT,
        region TEXT,
        salesperson TEXT
    )""")

    # --- Sample Data ---
    departments = [
        ("Engineering", 500000, "New York"),
        ("Marketing", 200000, "San Francisco"),
        ("HR", 150000, "Chicago"),
        ("Finance", 300000, "New York"),
        ("Sales", 250000, "Los Angeles"),
    ]
    cursor.executemany("INSERT INTO departments (name, budget, location) VALUES (?,?,?)", departments)

    employees = [
        ("Rahul Sharma", "rahul@company.com", 1, 85000, "2020-03-15", "Senior Engineer"),
        ("Priya Singh", "priya@company.com", 1, 72000, "2021-06-01", "Engineer"),
        ("Amit Kumar", "amit@company.com", 2, 65000, "2019-11-20", "Marketing Manager"),
        ("Sneha Patel", "sneha@company.com", 3, 55000, "2022-01-10", "HR Executive"),
        ("Vikram Rao", "vikram@company.com", 4, 90000, "2018-07-22", "Finance Lead"),
        ("Anita Desai", "anita@company.com", 5, 70000, "2021-03-05", "Sales Manager"),
        ("Ravi Verma", "ravi@company.com", 1, 95000, "2017-09-14", "Tech Lead"),
        ("Meena Iyer", "meena@company.com", 2, 60000, "2022-08-30", "Marketing Analyst"),
        ("Suresh Nair", "suresh@company.com", 4, 80000, "2020-05-18", "Accountant"),
        ("Kavitha Menon", "kavitha@company.com", 5, 68000, "2019-12-01", "Sales Rep"),
        ("Deepak Joshi", "deepak@company.com", 1, 78000, "2021-07-15", "Engineer"),
        ("Lakshmi Pillai", "lakshmi@company.com", 3, 52000, "2023-02-20", "HR Assistant"),
    ]
    cursor.executemany("INSERT INTO employees (name, email, department_id, salary, hire_date, role) VALUES (?,?,?,?,?,?)", employees)

    students = [
        ("Arjun Mehta", "CSE", 8.9, 3, "arjun@college.edu", "Mumbai"),
        ("Divya Krishnan", "ECE", 9.1, 2, "divya@college.edu", "Delhi"),
        ("Rohit Gupta", "CSE", 7.8, 4, "rohit@college.edu", "Bangalore"),
        ("Anjali Shah", "ME", 8.5, 1, "anjali@college.edu", "Chennai"),
        ("Karan Bose", "CSE", 9.3, 2, "karan@college.edu", "Kolkata"),
        ("Pooja Pillai", "IT", 8.0, 3, "pooja@college.edu", "Hyderabad"),
        ("Siddharth Rao", "ECE", 7.5, 4, "siddharth@college.edu", "Pune"),
        ("Nisha Patel", "CSE", 9.0, 1, "nisha@college.edu", "Ahmedabad"),
        ("Vishal Nair", "ME", 8.2, 2, "vishal@college.edu", "Jaipur"),
        ("Ritika Jain", "IT", 8.7, 3, "ritika@college.edu", "Mumbai"),
    ]
    cursor.executemany("INSERT INTO students (name, department, cgpa, year, email, city) VALUES (?,?,?,?,?,?)", students)

    sales = [
        ("Laptop", 85000, 10, "2024-01-15", "North", "Rahul Sharma"),
        ("Phone", 45000, 25, "2024-01-20", "South", "Anita Desai"),
        ("Tablet", 30000, 15, "2024-02-05", "East", "Kavitha Menon"),
        ("Laptop", 92000, 12, "2024-02-14", "West", "Rahul Sharma"),
        ("Headphones", 12000, 40, "2024-02-28", "North", "Anita Desai"),
        ("Phone", 50000, 30, "2024-03-10", "South", "Kavitha Menon"),
        ("Laptop", 78000, 8, "2024-03-22", "East", "Rahul Sharma"),
        ("Tablet", 35000, 20, "2024-04-01", "West", "Anita Desai"),
        ("Headphones", 15000, 50, "2024-04-15", "North", "Kavitha Menon"),
        ("Phone", 55000, 35, "2024-05-05", "South", "Rahul Sharma"),
        ("Laptop", 88000, 9, "2024-05-18", "East", "Anita Desai"),
        ("Tablet", 32000, 18, "2024-06-01", "West", "Kavitha Menon"),
    ]
    cursor.executemany("INSERT INTO sales (product, amount, quantity, sale_date, region, salesperson) VALUES (?,?,?,?,?,?)", sales)

    conn.commit()
    conn.close()
    print("✅ Sample database created successfully.")
