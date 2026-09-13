import sqlite3
import hashlib
from typing import Optional, Dict, Any

DB_NAME = "klick_diktat.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agencies (
        agency_id TEXT PRIMARY KEY,
        agency_name TEXT NOT NULL,
        subscription_plan TEXT DEFAULT 'BASIC',
        fonds_finanz_api_key TEXT DEFAULT '',
        is_active BOOLEAN DEFAULT 1
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        agency_id TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        FOREIGN KEY(agency_id) REFERENCES agencies(agency_id)
    )""")
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT OR IGNORE INTO agencies VALUES ('AG-100', 'Agentur Mustermann', 'BASIC', '', 1)")
        demo_pw = hashlib.sha256("makler123".encode()).hexdigest()
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('USER-1', 'AG-100', 'vater@makler.de', ?, 'ADMIN')", (demo_pw,))
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, u.agency_id, u.role, a.subscription_plan, a.is_active, a.fonds_finanz_api_key
        FROM users u JOIN agencies a ON u.agency_id = a.agency_id 
        WHERE u.email = ? AND u.password_hash = ?
    """, (email, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    if user and user[4]:
        return {"user_id": user[0], "agency_id": user[1], "role": user[2], "plan": user[3], "ff_api_key": user[5] if len(user) > 5 else ""}
    return None

def update_agency_api_key(agency_id: str, api_key: str):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE agencies SET fonds_finanz_api_key = ? WHERE agency_id = ?", (api_key, agency_id))
    conn.commit()
    conn.close()

init_db()