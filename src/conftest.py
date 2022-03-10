import contextlib
import pytest
from datetime import timedelta

from sqlalchemy import MetaData
from sqlalchemy.orm.session import Session

from fastapi.testclient import TestClient
from repository.models import User, VerificationCode

from settings import settings
from repository.database import SessionLocal, Base
from repository.crud.user import create_user, create_verification_code
from schemas.user import UserToCreateSchema

from main import app
from utils.authentication import create_jwt_token


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


def verify_user_by_id(db: Session, user: User):
    db.query(User).filter(User.id == user.id).update({"is_email_verified": True})
    db.commit()
    db.refresh(user)


@pytest.fixture
def regular_user(db):
    user = create_user(
        db,
        UserToCreateSchema(email="regular@test.test", password="password"),
    )
    verify_user_by_id(db, user)
    return user


@pytest.fixture
def email_not_verified_user(db):
    return create_user(
        db,
        UserToCreateSchema(
            email="unverified@test.test",
            password="password",
            is_email_verified=False,
        ),
    )


@pytest.fixture
def email_not_verified_user_verification_code(
    db: Session, email_not_verified_user: User
) -> VerificationCode:
    return create_verification_code(
        db,
        email_not_verified_user,
        timedelta(minutes=settings.signup_token_expires_minutes),
    )


@pytest.fixture
def email_already_verified_user(db: Session, email_not_verified_user: User) -> User:
    verify_user_by_id(db, email_not_verified_user)
    return email_not_verified_user


@pytest.fixture
def email_not_verified_user_signup_token(email_not_verified_user) -> str:
    return create_jwt_token(
        user_id=email_not_verified_user.id,
        expiration_timedelta=timedelta(minutes=settings.signup_token_expires_minutes),
        key=settings.secret_key,
        algorithm=settings.jwt_algorithm,
        issuer="/signup",
    )
