from datetime import timedelta
from pydantic import BaseSettings, Field


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


class JWTSettings(BaseSettings):
    algorithm: str = Field("HS256", const=True)
    access_expiration: timedelta = Field(timedelta(minutes=(60 * 24 * 3)), const=True)
    verify_email_expiration: timedelta = Field(timedelta(minutes=15), const=True)


class LoggingSettings(BaseSettings):
    level: str = "DEBUG"
    format: str = "%(levelname)s: %(name)s | %(message)s"
    handler: str = "console"

    @property
    def config(self) -> dict:
        return {
            "version": 1,
            "level": self.level,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": self.format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "loggers": {
                "api": {"handlers": [self.handler], "level": self.level},
            },
            "handlers": self.handlers,
        }

    @property
    def handlers(self) -> dict:
        return {
            "console": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "formatter": "default",
                "class": "logging.FileHandler",
                "filename": "api.log",
                "mode": "w",
            }
        }

    class Config:
        env_prefix = "API_LOGGING_"


class Settings(BaseSettings):
    project_name: str = Field("proper-FastAPI-startup", const=True)

    host: str = "localhost"
    port: int = 8000
    secret_key: str = "secret"
    allowed_origins_str: str = "*"

    @property
    def allowed_origins(self) -> list[str]:
        return [url for url in self.allowed_origins_str.split("|")]

    db: DBSettings = DBSettings()
    email: EmailSettings = EmailSettings()
    jwt: JWTSettings = JWTSettings()
    logging: LoggingSettings = LoggingSettings()

    class Config:
        env_prefix = "API_"


settings = Settings()
