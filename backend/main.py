from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import db_create

from .system.router import router as system_router
from .files.router import router as files_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_create()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(system_router)
app.include_router(files_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
