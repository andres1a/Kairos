from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base


def _build_database_url() -> str:
    database_url = os.getenv("KAIROS_DATABASE_URL")
    if database_url:
        return database_url

    database_path = Path(os.getenv("KAIROS_SQLITE_PATH", "kairos.db"))
    return f"sqlite:///{database_path.as_posix()}"


DATABASE_URL = _build_database_url()

engine_kwargs = {"future": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine: Engine = create_engine(DATABASE_URL, **engine_kwargs)


if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:  # type: ignore[override]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def init_db() -> None:
    """Crea todas las tablas registradas en el metadata de SQLAlchemy."""

    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope() -> Session:
    """Context manager simple para abrir y cerrar sesiones de base de datos."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
