import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid as uuid_lib

DB_DIR = '/app/data'
DB_PATH = os.path.join(DB_DIR, 'panel.db')

def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            uuid TEXT UNIQUE NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    try:
        conn = get_db()
        row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        conn.close()
        return row['value'] if row else default
    except Exception:
        return default

def set_setting(key, value):
    conn = get_db()
    conn.execute(
        'INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?',
        (key, value, value)
    )
    conn.commit()
    conn.close()

def is_setup_complete():
    try:
        conn = get_db()
        row = conn.execute('SELECT COUNT(*) as c FROM admin').fetchone()
        conn.close()
        return (row['c'] > 0) if row else False
    except Exception:
        return False

def create_admin(username, password):
    conn = get_db()
    conn.execute(
        'INSERT INTO admin (username, password_hash) VALUES (?, ?)',
        (username, generate_password_hash(password))
    )
    conn.commit()
    conn.close()

def verify_admin(username, password):
    try:
        conn = get_db()
        row = conn.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()
        conn.close()
        if row and check_password_hash(row['password_hash'], password):
            return True
        return False
    except Exception:
        return False

def get_all_users():
    try:
        conn = get_db()
        rows = conn.execute('SELECT * FROM users ORDER BY id DESC').fetchall()
        users = [dict(row) for row in rows]
        conn.close()
        return users
    except Exception:
        return []

def add_user(name):
    u_id = str(uuid_lib.uuid4())
    conn = get_db()
    conn.execute('INSERT INTO users (name, uuid) VALUES (?, ?)', (name, u_id))
    conn.commit()
    conn.close()
    return u_id

def delete_user(user_id):
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def toggle_user_status(user_id):
    conn = get_db()
    user = conn.execute('SELECT active FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        new_status = 0 if user['active'] == 1 else 1
        conn.execute('UPDATE users SET active = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
    conn.close()
