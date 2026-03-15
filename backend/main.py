from fastapi import FastAPI
from .system.router import router as system_router
from .files.router import router as files_router

app = FastAPI()

app.include_router(system_router)
app.include_router(files_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}