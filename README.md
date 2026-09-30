# Shortly

A full-stack URL shortener built with Flask, JavaScript, SQLite, and PostgreSQL. It lets users create shareable short links, choose a custom alias, and optionally set an expiration time.

**Live demo:** [urlshort-fhgq.onrender.com](https://urlshort-fhgq.onrender.com/)

## Why I built it

This project is a practical exercise in the backend and deployment fundamentals behind a small web application: validating untrusted input, persisting data, returning useful HTTP responses, handling conflicts, and testing important behavior.

## Features

- Shortens valid `http` and `https` URLs
- Supports optional custom aliases (3–32 letters, numbers, hyphens, or underscores)
- Offers link expiration: 1 hour, 24 hours, 7 days, or never
- Generates random short codes with Python's `secrets` module
- Handles alias conflicts with a clear `409 Conflict` response
- Displays dedicated pages for missing (`404`) and expired (`410`) links
- Uses a database-backed rate limit to reduce link-creation spam
- Uses SQLite for local development and PostgreSQL when `DATABASE_URL` is configured

## Tech stack

| Area | Technology |
| --- | --- |
| Backend | Python, Flask |
| Database | SQLite (local), PostgreSQL (production) |
| PostgreSQL driver | psycopg |
| Front end | HTML, CSS, JavaScript |
| Production server | Gunicorn |
| Tests | Python `unittest` |
| Hosting | Render |

## Project structure

```text
app.py              Flask application factory and HTTP routes
database.py         Database connections, schema setup, and SQL compatibility helpers
url_service.py      URL validation, alias validation, persistence, and redirects
rate_limit.py       Database-backed fixed-window rate limiter
templates/          Jinja HTML templates
static/css/         Site styles
static/js/          Browser behavior for form submission and copying links
static/favicon/     Browser and web-app icon assets
tests/              Automated application tests
```

## Run locally

Requirements: Python 3.10+ and PowerShell (commands below are for Windows).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser. Without any environment variables, the app creates and uses a local SQLite file named `database.db`.

## Configuration

The app is usable with no configuration locally. These optional environment variables are useful in deployment:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | local SQLite database | PostgreSQL connection string used in production |
| `RATE_LIMIT_SECRET` | development-only value | Secret used to hash client IP addresses before storing rate-limit keys |
| `RATE_LIMIT_MAX_REQUESTS` | `10` | Number of links an IP address may create per time window |
| `RATE_LIMIT_WINDOW_SECONDS` | `3600` | Rate-limit window in seconds; use `300` for five minutes |

Never commit `DATABASE_URL` or `RATE_LIMIT_SECRET`. Keep them in `.env` locally or in your host's environment-variable settings.

## API

### Create a link

`POST /api/shorten`

```json
{
  "original_url": "https://example.com/a-long-page",
  "custom_url": "example-link",
  "expires_in_hours": "24"
}
```

`custom_url` is optional. Send an empty `expires_in_hours` value for a link that does not expire.

A successful request returns `201 Created`:

```json
{
  "short_code": "example-link",
  "short_url": "https://your-domain.example/example-link"
}
```

Validation errors return `400`, an already-used alias returns `409`, and rate-limited requests return `429` with a `Retry-After` header.

## Tests

Run the automated tests with:

```powershell
python -m unittest discover -s tests
```

The current suite covers custom-link creation and redirects, invalid input, duplicate aliases, expired links, and rate limiting.

## Deployment notes

The deployed app runs on Render with PostgreSQL. Set `DATABASE_URL` in the Render web service to the Postgres instance's **internal** connection string, then redeploy. The schema is created automatically when the application starts.

Use the following production start command:

```text
gunicorn app:app
```

## Scope and future improvements

Shortly is a portfolio/demo project, not a production-grade public shortener. A production version would add authentication, link management, abuse reporting, observability, database migrations, stronger rate-limiting controls, and a dedicated cleanup strategy for expired links.
