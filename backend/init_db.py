"""
Create all database tables.

Run from the `backend` directory:
    python init_db.py

Use --reset to delete the existing database first (destroys all data).
"""

import argparse
from pathlib import Path

from app import models  # noqa: F401  -- must be imported so tables are registered
from app.config import DATABASE_DIR
from app.database import Base, engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tables created (existing tables were left untouched):")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"   - {table_name}")


def reset_database() -> None:
    db_file = Path(DATABASE_DIR) / "nutrition.db"
    if db_file.exists():
        engine.dispose()          # release the file handle before deleting
        db_file.unlink()
        print(f"Deleted existing database: {db_file}")
    else:
        print("No existing database found, creating a fresh one.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialise the project database.")
    parser.add_argument("--reset", action="store_true", help="Delete the database first.")
    args = parser.parse_args()

    if args.reset:
        reset_database()

    create_tables()
    print("\nDatabase initialisation complete.")