from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from jose import JWTError
from loguru import logger

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from schemas.auth import AuthenticatedUserSchema, TokenDataSchema

from settings import settings
from repository.database import SessionLocal
from repository.user import get_user_by_id
from domain.user import UserDomain

from utils.authentication import decode_jwt_token
from utils.hashing import IDHasher, get_hashid

import exceptions


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"v{settings.api_version}/login",
    scopes=settings.auth.public_scopes,
)
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
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db_session),
    id_hasher: IDHasher = Depends(get_id_hasher),
) -> AuthenticatedUserSchema:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    try:
        payload = TokenDataSchema(
            **decode_jwt_token(token, settings.secret_key, settings.auth.algorithm)
        )
        user_id = id_hasher.decode(payload.sub)
        user = get_user_by_id(session, user_id)
    except JWTError:
        raise exceptions.BadCredentials(headers={"WWW-Authenticate": authenticate_value})
    except NoResultFound:
        logger.trace(f"Authentication failed for unknown user {user_id}")
        raise exceptions.BadCredentials(headers={"WWW-Authenticate": authenticate_value})

    if not all(scope in payload.scopes for scope in security_scopes.scopes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return AuthenticatedUserSchema(user=user, token_payload=payload)


def get_user_domain(
    session: Session = Depends(get_db_session),
    id_hasher: IDHasher = Depends(get_id_hasher),
) -> UserDomain:
    return UserDomain(session=session, id_hasher=id_hasher)
