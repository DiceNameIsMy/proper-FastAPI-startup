from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from settings import settings

from api.router import router


# dictConfig(settings.logging.config)

app = FastAPI(title=settings.project_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/v1", tags=["v1"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
