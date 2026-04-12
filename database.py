import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

DB_NAME = "health_app.db"

def _get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_db()
    c = conn.cursor()
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Try adding new columns if they don't exist (schema migration)
    try:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'patient'")
        c.execute("ALTER TABLE users ADD COLUMN target_weight REAL DEFAULT 70.0")
        c.execute("ALTER TABLE users ADD COLUMN target_bmi REAL DEFAULT 22.0")
    except sqlite3.OperationalError:
        pass # Columns already exist
    # History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            age REAL,
            bp REAL,
            sugar REAL,
            cholesterol REAL,
            bmi REAL,
            health_score REAL,
            risk_pred TEXT,
            model_used TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, role='patient'):
    conn = _get_db()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                  (username, hash_password(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = _get_db()
    c = conn.cursor()
    c.execute('SELECT password_hash, role FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row and row['password_hash'] == hash_password(password):
        return True, row['role']
    return False, None

def get_user_profile(username):
    conn = _get_db()
    c = conn.cursor()
    c.execute('SELECT role, target_weight, target_bmi FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'role': row['role'], 'target_weight': row['target_weight'], 'target_bmi': row['target_bmi']}
    return None

def update_user_profile(username, target_weight, target_bmi):
    conn = _get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET target_weight = ?, target_bmi = ? WHERE username = ?',
              (target_weight, target_bmi, username))
    conn.commit()
    conn.close()

def insert_prediction(username, age, bp, sugar, cholesterol, bmi, health_score, risk_pred, model_used):
    conn = _get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO history (username, timestamp, age, bp, sugar, cholesterol, bmi, health_score, risk_pred, model_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, datetime.now().isoformat(), age, bp, sugar, cholesterol, bmi, health_score, risk_pred, model_used))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = _get_db()
    df = pd.read_sql_query('SELECT * FROM history WHERE username = ? ORDER BY timestamp ASC', conn, params=(username,))
    conn.close()
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def get_all_history():
    conn = _get_db()
    df = pd.read_sql_query('SELECT * FROM history ORDER BY timestamp DESC', conn)
    conn.close()
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df
