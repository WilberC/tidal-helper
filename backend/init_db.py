from app.core.db import validate_and_init_db


if __name__ == "__main__":
    print("Running database initialization script...")
    validate_and_init_db()
    print("Database initialization complete.")
