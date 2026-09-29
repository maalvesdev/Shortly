"""Application entry point for the URL shortener."""

from pathlib import Path
import os

from flask import Flask, jsonify, redirect, render_template, request

from database import close_db, init_db
from url_service import (
    AliasTakenError,
    InvalidAliasError,
    InvalidUrlError,
    create_short_url,
    get_destination,
)


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        # Render supplies DATABASE_URL in production. SQLite keeps local setup simple.
        DATABASE=os.environ.get("DATABASE_URL") or Path(__file__).with_name("database.db"),
        MAX_EXPIRY_HOURS=8_760,
    )
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.post("/api/shorten")
    def shorten_url():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return api_error("Send a JSON object in the request body.")
        try:
            short_code = create_short_url(
                data.get("original_url"),
                data.get("custom_url"),
                data.get("expires_in_hours"),
                app.config["MAX_EXPIRY_HOURS"],
            )
        except (InvalidUrlError, InvalidAliasError) as error:
            return api_error(str(error))
        except AliasTakenError:
            return api_error("That custom alias is already taken.", 409)
        return jsonify(short_code=short_code, short_url=f"{request.url_root}{short_code}"), 201

    @app.get("/<short_code>")
    def redirect_to_url(short_code):
        destination = get_destination(short_code)
        if destination is None:
            return render_template("not_found.html"), 404
        if destination == "expired":
            return render_template("expired.html"), 410
        return redirect(destination)

    return app


def api_error(message, status=400):
    return jsonify(error=message), status


app = create_app()


if __name__ == "__main__":
    app.run()
