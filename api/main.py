from fastapi import FastAPI
from .system.router import router as system_router

api = FastAPI()

api.include_router(system_router)

@api.get("/")
async def root():
    return {"message": "Hello World"}


