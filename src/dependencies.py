from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from jose import JWTError

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas.auth import AuthenticatedUserSchema

from settings import settings
from repository.database import SessionLocal
from repository.user import get_user_by_id
from domain.user import UserDomain

from utils.authentication import decode_jwt_token
from utils.hashing import IDHasher, get_hashid

import exceptions


oauth2_scheme = HTTPBearer()
id_hasher = get_hashid(settings.secret_key, min_length=10)


def get_db_session():
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_id_hasher() -> IDHasher:
    return id_hasher


async def authenticate(
    session: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    id_hasher: IDHasher = Depends(get_id_hasher),
) -> AuthenticatedUserSchema:
    try:
        payload = decode_jwt_token(
            token.credentials, settings.secret_key, settings.jwt.algorithm
        )
    except JWTError:
        raise exceptions.bad_credentials

    # TODO might raise unexpected exception
    user_id = id_hasher.decode(payload.get("sub", ""))
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
    if auth.token_payload.get("type") != "verify_email":
        raise exceptions.bad_credentials
    return auth


def get_user_domain(
    session: Session = Depends(get_db_session),
    id_hasher: IDHasher = Depends(get_id_hasher),
) -> UserDomain:
    return UserDomain(session=session, id_hasher=id_hasher)
