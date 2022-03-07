import contextlib
import pytest

from sqlalchemy import MetaData
from sqlalchemy.orm.session import Session

from fastapi.testclient import TestClient

from repository.database import SessionLocal, Base
from crud.user import create_user
from schemas.user import UserToCreateSchema

from main import app


meta = MetaData()


@pytest.fixture(autouse=True)
def teardown():
    """Clears out database after each test."""
    yield
    with contextlib.closing(SessionLocal()) as con:
        trans = con.begin()
        tables = ",".join(table.name for table in reversed(Base.metadata.sorted_tables))
        con.execute(f"TRUNCATE {tables};")
        trans.commit()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def db() -> Session:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def regular_user(db):
    return create_user(
        db, UserToCreateSchema(email="regular@test.test", password="password")
    )
