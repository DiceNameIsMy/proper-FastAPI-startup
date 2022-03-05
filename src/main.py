from fastapi import FastAPI

from settings import settings

from api.v1.router import router as v1_router


app = FastAPI(title=settings.project_name)
app.include_router(v1_router, prefix="/v1", tags=["v1"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
