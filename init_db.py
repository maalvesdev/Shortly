"""Create or update the local development database schema."""

from app import create_app


if __name__ == "__main__":
    create_app()
    print("Database is ready.")
