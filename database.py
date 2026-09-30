"""SQLite connection and schema helpers."""

import sqlite3
from flask import current_app, g

SCHEMA_STATEMENTS = (
    """CREATE TABLE IF NOT EXISTS urls (
    short_code TEXT PRIMARY KEY,
    original_url TEXT NOT NULL,
    expires_at INTEGER
)""",
    "CREATE INDEX IF NOT EXISTS idx_urls_expires_at ON urls (expires_at)",
    """CREATE TABLE IF NOT EXISTS rate_limits (
        client_key TEXT NOT NULL,
        window_started_at BIGINT NOT NULL,
        request_count INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (client_key, window_started_at)
    )""",
)


def get_db():
    """Return a request-scoped SQLite or PostgreSQL connection."""
    if "db" not in g:
        database = current_app.config["DATABASE"]
        if is_postgres(database):
            try:
                import psycopg
                from psycopg.rows import dict_row
            except ImportError as error:
                raise RuntimeError("PostgreSQL support requires psycopg.") from error
            connection = psycopg.connect(database, row_factory=dict_row)
        else:
            connection = sqlite3.connect(database)
            connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    connection = get_db()
    if is_postgres(current_app.config["DATABASE"]):
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
    else:
        connection.executescript(";".join(SCHEMA_STATEMENTS))
    connection.commit()


def execute(statement, parameters=()):
    """Run a parameterized statement using the driver's placeholder style."""
    if is_postgres(current_app.config["DATABASE"]):
        statement = statement.replace("?", "%s")
    return get_db().execute(statement, parameters)


def is_postgres(database):
    return isinstance(database, str) and database.startswith(("postgres://", "postgresql://"))


def is_integrity_error(error):
    """Return whether an error represents a unique or integrity constraint violation."""
    if isinstance(error, sqlite3.IntegrityError):
        return True
    try:
        from psycopg import IntegrityError
    except ImportError:
        return False
    return isinstance(error, IntegrityError)
