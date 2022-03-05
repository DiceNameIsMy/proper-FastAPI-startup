from sqlalchemy.orm.session import Session

from jose import JWTError

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from exceptions import credentials_exception
from repository.database import SessionLocal
from crud.user import get_user_by_id
from authentication import decode_jwt_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db_session() -> Session:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_current_user(
    session: Session = Depends(get_db_session),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt_token(token)
        user_id = int(payload.get("sub"))
        user = get_user_by_id(session, user_id)
    except JWTError:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user
