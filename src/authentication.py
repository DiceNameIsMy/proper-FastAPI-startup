from datetime import datetime, timedelta

from jose import jwt

from settings import settings


def create_access_token(user_id: int, data: dict = {}):
    to_encode = {"sub": str(user_id)} | data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
