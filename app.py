from flask import Flask, request
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ❌ Hardcoded secret
STRIPE_SECRET_KEY = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

# --- Auto-create database (so no extra file needed) ---
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        password TEXT
    )
    """)
    cursor.execute("INSERT OR IGNORE INTO users (id, user, password) VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()

init_db()


def execute_sql(query):
    conn = sqlite3.connect(os.getenv("DATABASE_URL", "users.db"))
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


# 🔴 SQL Injection (WORKING)
@app.route("/login")
def login():
    username = request.args.get("username")
    result = execute_sql(f"SELECT * FROM users WHERE user = '{username}'")
    if result:
        return "Login successful!"
    return "Login failed!"


# 🔴 Environment Leak
@app.route("/config")
def show_config():
    return dict(os.environ)


# 🔴 Path Traversal
@app.route("/read")
def read_file():
    filename = request.args.get("file")
    with open(filename, "r") as f:
        return f.read()


if __name__ == "__main__":
    app.run(debug=True)
