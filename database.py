"""SQLite connection and schema helpers."""

import sqlite3
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS urls (
    short_code TEXT PRIMARY KEY,
    original_url TEXT NOT NULL,
    expires_at INTEGER
);
CREATE INDEX IF NOT EXISTS idx_urls_expires_at ON urls (expires_at);
"""


def get_db():
    """Return the request-scoped SQLite connection."""
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    get_db().executescript(SCHEMA)
    get_db().commit()
