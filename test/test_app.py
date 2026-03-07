import os
import sys
import importlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


def make_app(db_path):
    os.environ['DB_NAME'] = str(db_path)
    if 'app' in sys.modules:
        del sys.modules['app']
    app = importlib.import_module('app')

    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute('''
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
    ''')
    conn.commit()
    conn.close()
    return app


def test_get_clients_empty(tmp_path):
    app = make_app(tmp_path / 'test.db')
    client = app.app.test_client()
    resp = client.get('/clients')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_add_and_get_client(tmp_path):
    app = make_app(tmp_path / 'test.db')
    client = app.app.test_client()

    import sqlite3
    conn = sqlite3.connect(str(tmp_path / 'test.db'))
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name, age, membership_status) VALUES (?,?,?)", ('alice', 30, 'Active'))
    conn.commit()
    conn.close()

    resp = client.get('/clients')
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(c['name'] == 'alice' for c in data)


def test_get_nonexistent_client(tmp_path):
    app = make_app(tmp_path / 'test.db')
    client = app.app.test_client()
    resp = client.get('/clients/nonexistent')
    assert resp.status_code == 404
