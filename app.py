import os
import sys
import sqlite3
import pickle
import subprocess
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ❌ Vulnerability 1: Hardcoded Secrets
JWT_SECRET_KEY = "sk_live_51MzFakeKeyNotRealForTestingOnly"
DATABASE_URL = os.getenv("DATABASE_URL", "users.db")


def init_database():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO accounts (id, username, password, role) VALUES (1, 'admin', 'SuperSecretAdmin123', 'admin')")
    conn.commit()
    conn.close()

init_database()


# 🔴 Vulnerability 2: SQL Injection (Direct string formatting in SQL query)
@app.route("/api/login", methods=["POST"])
def user_login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = f"SELECT id, username, role FROM accounts WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"status": "success", "user": user[1], "role": user[2]})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


# 🔴 Vulnerability 3: Command Injection (shell=True with unescaped input)
@app.route("/api/diagnostics/ping", methods=["GET"])
def system_ping():
    host = request.args.get("host", "127.0.0.1")
    cmd = f"ping -c 1 {host}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return jsonify({"output": res.stdout, "errors": res.stderr})


# 🔴 Vulnerability 4: Path Traversal (Arbitrary File Read)
@app.route("/api/files/read", methods=["GET"])
def read_log_file():
    filename = request.args.get("file", "app.log")
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    return jsonify({"file": filename, "content": content})


# 🔴 Vulnerability 5: Insecure Deserialization (pickle.loads on untrusted input)
@app.route("/api/session/restore", methods=["POST"])
def restore_session():
    token = request.form.get("token", "")
    if not token:
        return jsonify({"error": "No token provided"}), 400
    session_data = pickle.loads(bytes.fromhex(token))
    return jsonify({"session": str(session_data)})


# 🔴 Vulnerability 6: Environment / Secrets Exposure Endpoint
@app.route("/api/debug/config", methods=["GET"])
def debug_config():
    return jsonify(dict(os.environ))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
