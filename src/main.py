from fastapi import FastAPI

from settings import settings


app = FastAPI()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
