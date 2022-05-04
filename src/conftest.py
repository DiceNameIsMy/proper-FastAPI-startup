import contextlib
import pytest

from sqlalchemy import MetaData
from sqlalchemy.orm.session import Session

from fastapi.testclient import TestClient
from repository.models import User, VerificationCode

from settings import settings, oauth2_scopes
from repository.database import SessionLocal, Base
from domain.user import UserDomain
from schemas.user import UserInDbSchema, UserToCreateSchema

from main import app
from dependencies import id_hasher, jwt_client


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
def db():
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def user_domain(db: Session) -> UserDomain:
    return UserDomain(db, id_hasher, jwt_client)


@pytest.fixture
def unverified_user(user_domain: UserDomain):
    return user_domain.create(
        UserToCreateSchema(
            email="unverified_test@gmail.com",
            password="password",
            is_email_verified=False,
        )
    )


@pytest.fixture
def unverified_user_verification_code(
    user_domain: UserDomain, unverified_user: User
) -> VerificationCode:
    return user_domain.create_verification_code(unverified_user)


@pytest.fixture
def unverified_user_signup_token(unverified_user) -> str:
    return jwt_client.create_token(
        sub=id_hasher.encode(unverified_user.id),
        exp=settings.auth.verify_email_expiration,
        scopes=[oauth2_scopes.profile_verify[0]],
    )


@pytest.fixture
def verified_user(
    user_domain: UserDomain,
    unverified_user: User,
    unverified_user_verification_code: VerificationCode,
) -> User:
    user_domain.verify_email(
        UserInDbSchema.from_orm(unverified_user),
        unverified_user_verification_code.code,
    )
    return unverified_user


@pytest.fixture
def user_auth_token(verified_user) -> str:
    return jwt_client.create_token(
        sub=id_hasher.encode(verified_user.id),
        exp=settings.auth.access_expiration,
        scopes=[oauth2_scopes.profile_read[0], oauth2_scopes.profile_edit[0]],
    )


@pytest.fixture
def user_refresh_token(verified_user) -> str:
    return jwt_client.create_token(
        sub=id_hasher.encode(verified_user.id),
        exp=settings.auth.verify_email_expiration,
        scopes=[oauth2_scopes.token_refresh[0]],
    )
