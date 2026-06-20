import os
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default SQLite database URL if not overridden in the environment
DATABASE_URL = os.getenv("SLMFORGE_DB_URL", "sqlite:///./slmforge.db")

# Enable check_same_thread=False only for SQLite databases
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

def get_db() -> Generator:
    """Dependency for injecting database sessions into API routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
