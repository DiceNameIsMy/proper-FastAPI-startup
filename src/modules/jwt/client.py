from datetime import datetime, timedelta

from jose import jwt


class JWTClient:
    def __init__(
        self,
        private_key: str,
        public_key: str,
        algorithm: str | list[str],
    ):
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm

    def create_token(
        self,
        sub: str,
        exp: timedelta,
        scopes: list[str] = [],
    ) -> str:
        return self.encode(
            {"sub": sub, "exp": datetime.utcnow() + exp, "scopes": scopes}
        )

    def read_token(self, token: str) -> dict:
        return self.decode(token)

    def encode(self, data: dict) -> str:
        return jwt.encode(data, self.private_key, algorithm=self.algorithm)

    def decode(self, token: str, **kwargs) -> dict:
        return jwt.decode(
            token,
            self.public_key,
            algorithms=self.algorithm,
            options={
                "require_exp": True,
                "require_sub": True,
            },
            **kwargs
        )
