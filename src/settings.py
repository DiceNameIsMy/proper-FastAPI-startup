from datetime import timedelta
from enum import Enum

from pydantic import BaseSettings, Field


class PGSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5433
    user: str = "user"
    password: str = "pass"
    db: str = "database"
    driver: str = Field("postgresql", const=True)
    sslmode: str = "disable"
    sslrootcert: str = ""

    @property
    def url(self) -> str:
        return (
            f"{self.driver}://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.db}"
        )

    @property
    def args(self) -> dict:
        return {
            "sslmode": self.sslmode,
            "sslrootcert": self.sslrootcert,
        }

    class Config:
        env_prefix = "API_PG_"


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    user: str = ""
    password: str = ""
    driver: str = Field("redis", const=True)

    @property
    def url(self) -> str:
        return f"{self.driver}://{self.user}:{self.password}@" f"{self.host}:{self.port}"

    class Config:
        env_prefix = "API_REDIS_"


class EmailSettings(BaseSettings):
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    address: str = ""
    password: str = ""

    @property
    def is_configured(self) -> bool:
        return bool(self.address and self.password)

    class Config:
        env_prefix = "API_EMAIL_"


class AuthScope(Enum):
    profile_read = "Access current user"
    profile_edit = "Edit current user"
    profile_verify = "Verify current user"
    token_refresh = "Refresh token"


class AuthSettings(BaseSettings):
    scope: type[AuthScope] = Field(AuthScope, const=True)

    google_client_id: str = ""
    google_client_secret: str = ""
    google_allow_insecure: bool = True

    @property
    def private_scopes(cls) -> list[str]:
        return [cls.scope.profile_verify.name, cls.scope.token_refresh.name]

    @property
    def basic_scopes(cls) -> list[str]:
        return [cls.scope.profile_read.name]

    @property
    def oauth2_scopes_details(cls) -> dict[str, str]:
        return {
            name: obj.value
            for name, obj in cls.scope.__members__.items()
            if name not in cls.private_scopes  # type: ignore
        }

    class Config:
        env_prefix = "API_AUTH_"


class JWTSettings(BaseSettings):
    algorithm: str = Field("RS256", const=True)
    private_key: str = ""
    public_key: str = ""

    access_exp: timedelta = Field(timedelta(minutes=(60 * 24 * 3)), const=True)
    verify_email_exp: timedelta = Field(timedelta(minutes=15), const=True)

    class Config:
        env_prefix = "API_JWT_"
        secrets_dir = "/var/run/secrets"


class Settings(BaseSettings):
    project_name: str = Field("proper-FastAPI-startup", const=True)
    api_version: str = "1"
    use_idempotency: bool = False

    host: str = "localhost"
    port: str = "8000"
    secret_key: str = "secret"
    allowed_origins_str: str = "*"

    log_level: str = "INFO"
    log_file: str = ""

    sentry_dsn: str = ""
    environment: str = ""

    @property
    def allowed_origins(self) -> list[str]:
        return [url for url in self.allowed_origins_str.split("|")]

    # TODO use dsn types instead of classes
    pg = PGSettings()
    redis = RedisSettings()
    email = EmailSettings()
    auth = AuthSettings()
    jwt = JWTSettings()

    class Config:
        env_prefix = "API_"


settings = Settings()
oauth2_scope = settings.auth.scope
