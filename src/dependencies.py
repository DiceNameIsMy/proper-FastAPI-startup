from sqlalchemy.orm.session import Session

from jose import JWTError

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from schemas.auth import AuthenticatedUserSchema

from settings import settings
from repository.database import SessionLocal
from repository.crud.user import get_user_by_id
from utils.authentication import decode_jwt_token
from utils.email import EmailServer
from utils import exceptions


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/login")
email_server = EmailServer(
    smtp_server=settings.email.smtp_server,
    smtp_port=settings.email.smtp_port,
    email=settings.email.address,
    password=settings.email.password,
)


def get_db_session() -> Session:
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
        payload = decode_jwt_token(token, settings.secret_key, settings.jwt_algorithm)
    except JWTError:
        raise exceptions.bad_credentials

    user_id = int(payload.get("sub"))
    user = get_user_by_id(session, user_id)
    if user is None:
        raise exceptions.bad_credentials
    return AuthenticatedUserSchema(user=user, token_payload=payload)


def get_email_server() -> EmailServer:
    return email_server
