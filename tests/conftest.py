import pytest
from database import db as db_module


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))
    db_module.init_db()
    yield


@pytest.fixture
def seed_user_id():
    from werkzeug.security import generate_password_hash
    conn = db_module.get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123"), "2026-01-01 00:00:00"),
    )
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        [
            (user_id, 45.50,  "Food",          "2026-05-02", "Grocery run"),
            (user_id, 18.00,  "Transport",     "2026-05-05", "Uber to office"),
            (user_id, 120.00, "Bills",         "2026-05-07", "Electricity bill"),
            (user_id, 60.00,  "Health",        "2026-05-10", "Pharmacy"),
            (user_id, 35.00,  "Entertainment", "2026-05-13", "Netflix + Spotify"),
            (user_id, 89.99,  "Shopping",      "2026-05-16", "New shoes"),
            (user_id, 22.75,  "Other",         "2026-05-19", "Miscellaneous"),
            (user_id, 12.50,  "Food",          "2026-05-22", "Coffee and snacks"),
        ],
    )
    conn.commit()
    conn.close()
    return user_id


@pytest.fixture
def empty_user_id():
    from werkzeug.security import generate_password_hash
    conn = db_module.get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Empty User", "empty@spendly.com", generate_password_hash("password123")),
    )
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return user_id


@pytest.fixture
def client():
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.test_client() as c:
        yield c
