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

    # Clients table (core)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        age INTEGER,
        height REAL,
        weight REAL,
        program TEXT,
        calories INTEGER,
        target_weight REAL,
        target_adherence INTEGER,
        membership_status TEXT,
        membership_end TEXT
    )
    """)

    # Default to admin user
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", ('admin', 'admin', 'Admin'))

    conn.commit()
    conn.close()

def list_clients():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, height, weight, program, calories, membership_status FROM clients ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "name": r[1],
            "age": r[2],
            "height": r[3],
            "weight": r[4],
            "program": r[5],
            "calories": r[6],
            "membership_status": r[7],
        })
    return out

def get_client(name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, height, weight, program, calories, membership_status FROM clients WHERE name=?", (name,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "age": row[2],
        "height": row[3],
        "weight": row[4],
        "program": row[5],
        "calories": row[6],
        "membership_status": row[7],
    }

def add_client(name, age=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name, age, membership_status) VALUES (?,?,?)", (name, age, 'Active'))
    conn.commit()
    conn.close()

# Flask application
app = Flask(__name__)
init_db()

@app.route("/clients", methods=["GET"])
def clients_get():
    return jsonify(list_clients()), 200

@app.route("/clients/<string:name>", methods=["GET"])
def clients_get_one(name):
    c = get_client(name)
    if not c:
        return jsonify({"error": "client not found"}), 404
    return jsonify(c), 200

@app.route("/clients", methods=["POST"])
def clients_post():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name")
    age = data.get("age")
    if not name:
        return jsonify({"error": "'name' is required"}), 400
    try:
        add_client(name, age)
    except sqlite3.IntegrityError:
        return jsonify({"error": "client already exists"}), 409
    return jsonify({"message": "client added", "name": name}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
