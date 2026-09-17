"""
Database engine, session factory, and the declarative Base class.

Every ORM model inherits from `Base`. Every API endpoint that needs the
database asks for a session via the `get_db` dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# check_same_thread=False is required for SQLite + FastAPI, because FastAPI
# may handle a single request across more than one thread. This is safe here
# since each request gets its own short-lived session.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # set True to print every SQL statement (useful for debugging)
)

# A factory that produces new database sessions.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# All ORM models inherit from this.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session and always closes it.

    Usage in a router:
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()