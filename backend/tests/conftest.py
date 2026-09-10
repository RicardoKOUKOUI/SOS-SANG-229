"""Pytest fixtures. SQLite is used so matching + endpoints run without secrets."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import Base

_POSTGRES_ONLY_DEFAULTS = ("gen_random_uuid()",)


def _strip_postgres_only_defaults() -> None:
    """Drop Postgres-only DDL defaults so SQLite ``create_all`` can run.

    Production still uses ``gen_random_uuid()`` via Alembic. Tests set PKs
    explicitly (or rely on application ``uuid4()``).
    """
    for table in Base.metadata.tables.values():
        for column in table.columns:
            default = column.server_default
            if default is None:
                continue
            arg = getattr(default, "arg", None)
            if arg is not None and str(arg) in _POSTGRES_ONLY_DEFAULTS:
                column.server_default = None


_strip_postgres_only_defaults()


@pytest.fixture
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _configure_sqlite(dbapi_connection, _connection_record):  # noqa: ANN001
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def api_client() -> TestClient:
    """HTTP client without a database (health / OpenAPI)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
