from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db, create_user, get_user_by_email

app = Flask(__name__)
app.secret_key = "dev-secret-change-in-prod"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if len(name) < 2:
        return render_template("register.html", error="Name must be at least 2 characters.")
    if not email:
        return render_template("register.html", error="Email address is required.")
    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")
    if get_user_by_email(email) is not None:
        return render_template("register.html", error="An account with that email already exists.")

    password_hash = generate_password_hash(password)
    user_id = create_user(name, email, password_hash)
    session["user_id"] = user_id
    session["user_name"] = name
    return redirect(url_for("landing"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error="Email and password are required.")

    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": session.get("user_name", "Demo User"),
        "email": "demo@spendly.com",
        "member_since": "January 2026",
    }
    stats = {
        "total_spent": 403.74,
        "transaction_count": 8,
        "top_category": "Bills",
    }
    transactions = [
        {"date": "2026-05-22", "description": "Coffee and snacks",  "category": "Food",          "amount": 12.50},
        {"date": "2026-05-19", "description": "Miscellaneous",       "category": "Other",         "amount": 22.75},
        {"date": "2026-05-16", "description": "New shoes",           "category": "Shopping",      "amount": 89.99},
        {"date": "2026-05-13", "description": "Netflix + Spotify",   "category": "Entertainment", "amount": 35.00},
        {"date": "2026-05-10", "description": "Pharmacy",            "category": "Health",        "amount": 60.00},
    ]
    categories = [
        {"name": "Bills",         "amount": 120.00, "pct": 30},
        {"name": "Shopping",      "amount":  89.99, "pct": 22},
        {"name": "Health",        "amount":  60.00, "pct": 15},
        {"name": "Food",          "amount":  58.00, "pct": 14},
        {"name": "Other",         "amount":  22.75, "pct":  6},
        {"name": "Entertainment", "amount":  35.00, "pct":  9},
        {"name": "Transport",     "amount":  18.00, "pct":  4},
    ]
    return render_template("profile.html",
                           user=user, stats=stats,
                           transactions=transactions, categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
