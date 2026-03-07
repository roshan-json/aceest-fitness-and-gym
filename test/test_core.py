import os
import sys
import importlib
import sqlite3


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


def import_app_with_db(db_path):
    os.environ['DB_NAME'] = str(db_path)
    if 'app' in sys.modules:
        del sys.modules['app']
    return importlib.import_module('app')


def table_exists(db_path, table_name):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def test_init_db_creates_tables(tmp_path):
    db = tmp_path / 'core_init.db'
    app = import_app_with_db(db)

    # core tables from legacy app
    for t in ('users', 'clients', 'progress', 'workouts', 'exercises', 'metrics'):
        assert table_exists(db, t), f"expected table {t} to exist"


def test_add_and_get_client_core(tmp_path):
    db = tmp_path / 'core_client.db'
    app = import_app_with_db(db)

    # add client via core function
    app.add_client('alice', 30)
    c = app.get_client('alice')
    assert c is not None
    assert c['name'] == 'alice'
    assert c['age'] == 30


def test_duplicate_add_raises(tmp_path):
    db = tmp_path / 'core_dup.db'
    app = import_app_with_db(db)
    app.add_client('bob', 25)
    try:
        # second insert should raise IntegrityError
        app.add_client('bob', 25)
        raised = False
    except sqlite3.IntegrityError:
        raised = True
    assert raised, 'expected sqlite3.IntegrityError on duplicate add'


def test_generate_program_updates_client(tmp_path):
    db = tmp_path / 'core_prog.db'
    app = import_app_with_db(db)
    # Add client and generate program
    app.add_client('carol', 29)
    program = app.generate_program_for_client('carol')
    assert program is not None and isinstance(program, str)
    # client record should now include program
    c = app.get_client('carol')
    assert c.get('program') == program
