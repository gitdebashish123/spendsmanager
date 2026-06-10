# Spec: Registration

## Overview
This step wires up the registration form so new users can create a Spendly account. The `GET /register` route already renders the form; this step adds the `POST /register` handler that validates input, hashes the password, inserts the user into the database, opens a session, and redirects to the dashboard (or back to the form with an error message). It also adds `create_user()` to `database/db.py` and sets `app.secret_key` so Flask sessions work.

## Depends on
- Step 1 — Database setup (`users` table must exist, `get_db()` must be implemented)

## Routes
- `POST /register` — validates form data, creates user, starts session, redirects — public

## Database changes
No new tables or columns. The `users` table from Step 1 is sufficient.

A new helper is added to `database/db.py`:
- `create_user(name, email, password_hash)` — inserts a row and returns the new `id`
- `get_user_by_email(email)` — fetches a user row by email for duplicate-check

## Templates
- **Modify:** `templates/register.html`
  - Fix hardcoded `action="/register"` → `action="{{ url_for('register') }}"`
  - Keep the existing `{% if error %}` error block as-is (already present)
  - No other template changes needed

## Files to change
- `app.py` — add `request`, `session`, `redirect`, `url_for` to Flask imports; add `app.secret_key`; implement `POST /register` handler inside the existing `register()` view (methods list)
- `database/db.py` — add `create_user()` and `get_user_by_email()` helpers
- `templates/register.html` — fix hardcoded form action URL

## Files to create
None.

## New dependencies
No new pip packages. `werkzeug.security.generate_password_hash` is already available.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders — never f-strings in SQL)
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py` — the route function only calls helpers
- Use `abort()` for unexpected HTTP errors; pass `error=` to `render_template` for form validation failures (not `flash`)
- `app.secret_key` must be set before any session usage; use a hard-coded dev string for now (e.g. `"dev-secret-change-in-prod"`)
- After successful registration: set `session["user_id"]` and `session["user_name"]`, then redirect to `/` (landing) until a dashboard exists
- Validation rules:
  - name: required, strip whitespace, min 2 chars
  - email: required, strip whitespace, check uniqueness
  - password: required, min 8 chars

## Definition of done
- [ ] Submitting the form with valid data creates a new row in the `users` table (verifiable with `sqlite3 spendly.db "SELECT * FROM users;"`)
- [ ] After successful registration, the browser is redirected (HTTP 302) — not left on `/register`
- [ ] Submitting with a duplicate email re-renders the form with a visible error message (no crash)
- [ ] Submitting with a short password (< 8 chars) re-renders the form with a visible error message
- [ ] Submitting with an empty name re-renders the form with a visible error message
- [ ] Password stored in DB is a hash, not plain text
- [ ] `session["user_id"]` is set after successful registration (verifiable via Flask debug toolbar or a quick print in a subsequent route)
- [ ] App starts without errors on `python app.py`
