from datetime import timedelta
from pydantic import BaseSettings, BaseModel, Field


class DBSettings(BaseSettings):
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


class AuthScopes(BaseModel):
    profile_read: tuple[str, str] = "profile:read", "Access current user"
    profile_edit: tuple[str, str] = "profile:edit", "Edit current user"
    profile_verify: tuple[str, str] = "profile:verify", "Verify current user"
    token_refresh: tuple[str, str] = "token:refresh", "Refresh token"

    _private_scopes: set[str] = {"profile:verify", "token:refresh"}

    @property
    def oauth2_format(self) -> dict:
        return {
            scope[0]: scope[1]
            for _, scope in self.dict().items()
            if scope[0] not in self._private_scopes
        }


class AuthSettings(BaseSettings):
    algorithm: str = Field("HS256", const=True)
    access_expiration: timedelta = Field(timedelta(minutes=(60 * 24 * 3)), const=True)
    verify_email_expiration: timedelta = Field(timedelta(minutes=15), const=True)
    scopes: AuthScopes = AuthScopes()


class Settings(BaseSettings):
    project_name: str = Field("proper-FastAPI-startup", const=True)
    api_version: str = "1"

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

    db: DBSettings = DBSettings()
    email: EmailSettings = EmailSettings()
    auth: AuthSettings = AuthSettings()

    class Config:
        env_prefix = "API_"


settings = Settings()
oauth2_scopes: AuthScopes = settings.auth.scopes
