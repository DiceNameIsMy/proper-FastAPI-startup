import sys

from loguru import logger
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from settings import settings

from api.router import router


logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
)
if settings.log_file:
    logger.add(
        settings.log_file,
        level=settings.log_level,
        rotation="10 KB",
        compression="zip",
    )

logger.info(f"Starting API server at http://{settings.host}:{settings.port}")
app = FastAPI(title=settings.project_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)
    app.add_middleware(SentryAsgiMiddleware)


app.include_router(
    router, prefix=f"/v{settings.api_version}", tags=[settings.api_version]
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port, log_level="critical")
