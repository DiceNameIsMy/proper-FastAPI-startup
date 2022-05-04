from datetime import datetime, timedelta

from jose import jwt


class JWTClient:
    def __init__(
        self,
        secret_key: str,
        expiration: timedelta,
        algorithm: str | list[str],
    ):
        self.key = secret_key
        self.exp = expiration
        self.algorithm = algorithm

    def create_token(
        self,
        sub: str,
        scopes: list[str] = [],
        exp: timedelta | None = None,
    ) -> str:
        return self.encode(
            {"sub": sub, "exp": datetime.utcnow() + (exp or self.exp), "scopes": scopes}
        )

    def read_token(self, token: str) -> dict:
        return self.decode(token)

    def encode(self, data: dict) -> str:
        return jwt.encode(data, self.key, algorithm=self.algorithm)

    def decode(self, token: str, **kwargs) -> dict:
        return jwt.decode(
            token,
            self.key,
            algorithms=self.algorithm,
            options={
                "require_exp": True,
                "require_sub": True,
            },
            **kwargs
        )
