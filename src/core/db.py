
import os
import sqlite3


def _db_name():
    """Return current DB file name from env; read at call time so tests can change
    DB_NAME between imports.
    """
    return os.getenv("DB_NAME", "aceest_fitness.db")


def get_conn():
    return sqlite3.connect(str(_db_name()), check_same_thread=False)


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

    # Progress table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        week TEXT,
        adherence INTEGER
    )
    """)

    # Workouts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        date TEXT,
        workout_type TEXT,
        duration_min INTEGER,
        notes TEXT
    )
    """)

    # Exercises
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER,
        name TEXT,
        sets INTEGER,
        reps INTEGER,
        weight REAL
    )
    """)

    # Metrics
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        date TEXT,
        weight REAL,
        waist REAL,
        bodyfat REAL
    )
    """)

    # Default to admin user
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", ('admin', 'admin', 'Admin'))

    conn.commit()
    conn.close()


program_templates = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"]
}


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


def generate_program_for_client(name):
    client = get_client(name)
    if not client:
        return None
    cats = list(program_templates.keys())
    choice = cats[hash(name) % len(cats)]
    program = program_templates[choice][0]
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE clients SET program=? WHERE name=?", (program, name))
    conn.commit()
    conn.close()
    return program
