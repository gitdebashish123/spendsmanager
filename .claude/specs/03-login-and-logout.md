# Spec: Login and Logout

## Overview
This step wires up the login form and logout route. The `GET /login` route already renders the form; this step adds the `POST /login` handler that validates credentials, verifies the password hash, opens a session, and redirects to the landing page (or re-renders the form with an error on failure). It also replaces the `/logout` stub with a real handler that clears the session and redirects to the landing page. No new database tables are required — `get_user_by_email()` from Step 1 is sufficient for credential lookup.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`, `get_user_by_email()`)
- Step 2 — Registration (`app.secret_key` set, session pattern established with `session["user_id"]` and `session["user_name"]`)

## Routes
- `POST /login` — validates credentials, verifies password hash, starts session, redirects — public
- `GET /logout` — clears session, redirects to landing — public (safe to call when not logged in)

## Database changes
No database changes.

`get_user_by_email(email)` already exists in `database/db.py` and is sufficient for credential lookup — no new helpers needed.

## Templates
- **Modify:** `templates/login.html`
  - Ensure `<form>` uses `action="{{ url_for('login') }}"` and `method="POST"` — not hardcoded URLs
  - Add error display block if not already present:
    ```html
    {% if error %}
    <p class="error">{{ error }}</p>
    {% endif %}
    ```

## Files to change
- `app.py`
  - Add `check_password_hash` to the `werkzeug.security` import line (currently only `generate_password_hash` is imported)
  - Add `methods=["GET", "POST"]` to the `login()` view and implement the `POST` handler
  - Replace the `/logout` stub body with real session-clearing logic
- `templates/login.html` — fix form action, confirm method is POST, add error block

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is already available (same package as `generate_password_hash`).

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders — never f-strings in SQL)
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plain text
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py` — route functions only call helpers
- Use `render_template(..., error=...)` for form validation failures — not `flash()`
- Login validation:
  - email: required, strip whitespace
  - password: required
  - If email not found OR password mismatch → same generic error: `"Invalid email or password."` — never reveal which field is wrong
- After successful login: set `session["user_id"]` and `session["user_name"]`, redirect to `url_for("landing")`
- Logout must call `session.clear()` (not `session.pop`) then redirect to `url_for("landing")`

## Definition of done
- [ ] Submitting the form with valid credentials redirects (HTTP 302) to the landing page
- [ ] `session["user_id"]` and `session["user_name"]` are set after successful login
- [ ] Submitting with an unknown email re-renders `/login` with a visible generic error (no crash)
- [ ] Submitting with the correct email but wrong password shows the same generic error
- [ ] Submitting with empty fields re-renders the form with a visible error
- [ ] Visiting `/logout` clears the session and redirects to the landing page
- [ ] Visiting `/logout` when not logged in does not crash — redirects cleanly
- [ ] App starts without errors on `python app.py`
