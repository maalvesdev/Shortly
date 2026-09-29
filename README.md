# URL Shortener

A small URL shortener built to demonstrate practical Flask fundamentals: application factories, input validation, SQLite persistence, HTTP status codes, and automated tests.

## Features

- Shorten valid `http` and `https` URLs
- Create optional aliases using safe, URL-friendly characters
- Choose an expiration time or keep a link permanently
- Helpful 404 and expired-link pages
- Theme preference and one-click copy in a responsive, accessible UI
- Random codes generated with `secrets`, with collision handling

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

## Notes for deployment

SQLite is deliberately used for this single-instance portfolio project. For a multi-instance deployment, use a managed database and configure the database path/URL through environment-specific settings. Run a production WSGI server with `gunicorn app:app`; do not use Flask's development server in production.
