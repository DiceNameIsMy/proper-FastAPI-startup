from datetime import datetime, timedelta

from jose import jwt


def create_access_token(
    user_id: int, expiration_timedelta: timedelta, key: str, algorithm: str | list[str]
) -> str:
    to_encode = {"sub": str(user_id)}
    expire = datetime.utcnow() + expiration_timedelta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, key, algorithm=algorithm
    )
    return encoded_jwt


def decode_jwt_token(token: str, key: str, algorithm: str | list[str]) -> dict:
    return jwt.decode(token, key, algorithms=algorithm)
