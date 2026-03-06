import os
import sqlite3
from flask import Flask, jsonify, request

# DB config
DB_NAME = os.getenv("DB_NAME", "aceest_fitness.db")


def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    # Default to admin user
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", ('admin', 'admin', 'Admin'))

    conn.commit()
    conn.close()

# Flask application
app = Flask(__name__)
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
