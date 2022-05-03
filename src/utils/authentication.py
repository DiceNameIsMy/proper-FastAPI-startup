from datetime import datetime, timedelta

from jose import jwt


def create_jwt_token(
    user_id_hash: str,
    expiration_timedelta: timedelta,
    key: str,
    algorithm: str | list[str],
    scopes: list[str] = [],
) -> str:
    expire = datetime.utcnow() + expiration_timedelta
    to_encode = {
        "sub": user_id_hash,
        "exp": expire,
        "scopes": scopes
    }
    encoded_jwt = jwt.encode(to_encode, key, algorithm=algorithm)
    return encoded_jwt


def decode_jwt_token(token: str, key: str, algorithm: str | list[str]) -> dict:
    return jwt.decode(token, key, algorithms=algorithm)
