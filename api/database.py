from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def _default_sqlite_url() -> str:
    # Store DB file inside `api/` folder
    db_path = Path(__file__).resolve().parent / "diagnoze.sqlite3"
    return f"sqlite:///{db_path.as_posix()}"


DATABASE_URL = _default_sqlite_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # sqlite
    pool_pre_ping=True,
)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so Base.metadata is populated
    from . import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)

