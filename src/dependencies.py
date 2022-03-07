from sqlalchemy.orm.session import Session

from jose import JWTError

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from settings import settings
from repository.database import SessionLocal
from repository.models import User
from crud.user import get_user_by_id
from utils.authentication import decode_jwt_token
from utils import exceptions


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/login")


def get_db_session() -> Session:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_current_user(
    session: Session = Depends(get_db_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_jwt_token(token, settings.secret_key, settings.jwt_algorithm)
        user_id = int(payload.get("sub"))
    except JWTError:
        raise exceptions.bad_credentials

    user = get_user_by_id(session, user_id)
    if user is None:
        raise exceptions.bad_credentials
    return user
