import pytest
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown,
)


# ── get_user_by_id ────────────────────────────────────────────────────

def test_get_user_by_id_valid(seed_user_id):
    result = get_user_by_id(seed_user_id)
    assert result is not None
    assert result["name"] == "Demo User"
    assert result["email"] == "demo@spendly.com"
    assert result["member_since"] == "January 2026"


def test_get_user_by_id_nonexistent():
    assert get_user_by_id(99999) is None


# ── get_summary_stats ─────────────────────────────────────────────────

def test_get_summary_stats_with_expenses(seed_user_id):
    result = get_summary_stats(seed_user_id)
    assert result["total_spent"] == pytest.approx(403.74, abs=0.01)
    assert result["transaction_count"] == 8
    assert result["top_category"] == "Bills"


def test_get_summary_stats_no_expenses(empty_user_id):
    result = get_summary_stats(empty_user_id)
    assert result["total_spent"] == 0
    assert result["transaction_count"] == 0
    assert result["top_category"] == "—"


# ── get_recent_transactions ───────────────────────────────────────────

def test_get_recent_transactions_with_expenses(seed_user_id):
    result = get_recent_transactions(seed_user_id)
    assert len(result) == 8
    assert result[0]["date"] == "2026-05-22"
    assert result[-1]["date"] == "2026-05-02"
    for tx in result:
        assert {"date", "description", "category", "amount"} <= tx.keys()


def test_get_recent_transactions_limit(seed_user_id):
    result = get_recent_transactions(seed_user_id, limit=3)
    assert len(result) == 3
    assert result[0]["date"] == "2026-05-22"


def test_get_recent_transactions_no_expenses(empty_user_id):
    assert get_recent_transactions(empty_user_id) == []


# ── get_category_breakdown ────────────────────────────────────────────

def test_get_category_breakdown_with_expenses(seed_user_id):
    result = get_category_breakdown(seed_user_id)
    assert len(result) == 7
    assert result[0]["name"] == "Bills"
    assert result[0]["amount"] == pytest.approx(120.00, abs=0.01)
    pcts = [item["pct"] for item in result]
    assert all(isinstance(p, int) for p in pcts)
    assert sum(pcts) == 100
    for cat in result:
        assert {"name", "amount", "pct"} <= cat.keys()


def test_get_category_breakdown_no_expenses(empty_user_id):
    assert get_category_breakdown(empty_user_id) == []


# ── GET /profile route ────────────────────────────────────────────────

def test_profile_unauthenticated_redirects(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_authenticated_returns_200(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
        sess["user_name"] = "Demo User"
    assert client.get("/profile").status_code == 200


def test_profile_shows_user_info(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
        sess["user_name"] = "Demo User"
    body = client.get("/profile").data.decode("utf-8")
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "January 2026" in body


def test_profile_shows_rupee_symbol(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
        sess["user_name"] = "Demo User"
    assert "₹" in client.get("/profile").data.decode("utf-8")


def test_profile_total_spent(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
        sess["user_name"] = "Demo User"
    assert "403.74" in client.get("/profile").data.decode("utf-8")


def test_profile_top_category(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
        sess["user_name"] = "Demo User"
    assert "Bills" in client.get("/profile").data.decode("utf-8")


def test_profile_transaction_order(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
        sess["user_name"] = "Demo User"
    body = client.get("/profile").data.decode("utf-8")
    assert body.index("2026-05-22") < body.index("2026-05-02")


def test_profile_all_categories_present(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
        sess["user_name"] = "Demo User"
    body = client.get("/profile").data.decode("utf-8")
    for cat in ["Bills", "Shopping", "Health", "Food", "Entertainment", "Other", "Transport"]:
        assert cat in body


def test_profile_empty_user_no_crash(client, empty_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = empty_user_id
        sess["user_name"] = "Empty User"
    response = client.get("/profile")
    assert response.status_code == 200
    assert "0.00" in response.data.decode("utf-8")
