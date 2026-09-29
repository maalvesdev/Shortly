# URL Shortener

A small URL shortener built to demonstrate practical Flask fundamentals: application factories, input validation, SQLite persistence, HTTP status codes, and automated tests.

## Features

- Shorten valid `http` and `https` URLs
- Create optional aliases using safe, URL-friendly characters
- Choose an expiration time or keep a link permanently
- Helpful 404 and expired-link pages
- Theme preference and one-click copy in a responsive, accessible UI
- Random codes generated with `secrets`, with collision handling
- Database-backed rate limiting: 10 new links per IP address per hour

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000`.

## Test

```powershell
python -m unittest discover -s tests
```

## Project structure

```text
app.py           Flask application factory and routes
database.py      Request-scoped SQLite connection and schema
url_service.py   Validation and link persistence rules
templates/       Server-rendered pages
static/          CSS and browser JavaScript
tests/           Automated regression tests
```

## Database and deployment

Local development uses SQLite automatically, so there is no database setup before running the app. In production, set the `DATABASE_URL` environment variable to a PostgreSQL connection string. The app detects it, connects with `psycopg`, and creates the `urls` table and index on startup.

For Render: create a Postgres instance in the same region as the web service, then set the web service's `DATABASE_URL` to the database's **internal** connection string and redeploy. Never commit this connection string: it contains credentials.

The shortener also rate-limits creation requests. Set `RATE_LIMIT_SECRET` to a generated secret in Render's Environment page; it is used to hash client IP addresses before recording a rate-limit bucket. Set `RATE_LIMIT_MAX_REQUESTS` to change the default limit of 10 and `RATE_LIMIT_WINDOW_SECONDS` to change the default one-hour window (use `300` for five minutes).

Run the app in production with `gunicorn app:app`; do not use Flask's development server.
