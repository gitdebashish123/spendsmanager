import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spendly.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash)
    )
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    expenses = [
        (user_id, 45.50,  "Food",          "2026-05-02", "Grocery run"),
        (user_id, 18.00,  "Transport",     "2026-05-05", "Uber to office"),
        (user_id, 120.00, "Bills",         "2026-05-07", "Electricity bill"),
        (user_id, 60.00,  "Health",        "2026-05-10", "Pharmacy"),
        (user_id, 35.00,  "Entertainment", "2026-05-13", "Netflix + Spotify"),
        (user_id, 89.99,  "Shopping",      "2026-05-16", "New shoes"),
        (user_id, 22.75,  "Other",         "2026-05-19", "Miscellaneous"),
        (user_id, 12.50,  "Food",          "2026-05-22", "Coffee and snacks"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses
    )
    conn.commit()
    conn.close()
