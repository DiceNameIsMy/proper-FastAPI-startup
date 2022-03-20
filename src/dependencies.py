from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from jose import JWTError

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from schemas.auth import AuthenticatedUserSchema

from settings import settings
from repository.database import SessionLocal
from repository.crud.user import get_user_by_id
from domain.user import UserDomain
from utils.authentication import decode_jwt_token
import exceptions


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/login")


def get_db_session():
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def authenticate(
    session: Session = Depends(get_db_session),
    token: str = Depends(oauth2_scheme),
) -> AuthenticatedUserSchema:
    try:
        payload = decode_jwt_token(token, settings.secret_key, settings.jwt.algorithm)
    except JWTError:
        raise exceptions.bad_credentials

    user_id = int(payload.get("sub", 0))
    try:
        user = get_user_by_id(session, user_id)
        return AuthenticatedUserSchema(user=user, token_payload=payload)
    except NoResultFound:
        raise exceptions.bad_credentials


def authenticate_access_token(
    auth: AuthenticatedUserSchema = Depends(authenticate),
) -> AuthenticatedUserSchema:
    if auth.token_payload.get("type") != "access":
        raise exceptions.bad_credentials
    return auth


def authenticate_verify_email_token(
    auth: AuthenticatedUserSchema = Depends(authenticate),
) -> AuthenticatedUserSchema:
    if auth.token_payload.get("type") != "verify-email":
        raise exceptions.bad_credentials
    return auth


def get_user_domain(session: Session = Depends(get_db_session)) -> UserDomain:
    return UserDomain(session=session)
