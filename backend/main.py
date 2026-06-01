from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import logging
import logging.config
from .log_config import LOG_CONFIG, LogConsoleFormatter

from .database import db_create
from .config import settings

from .system.router import router as system_router
from .files.router import router as files_router
from .tags.router import router as tags_router
from .file_tags.router import router as file_tags_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.config.dictConfig(LOG_CONFIG)
    
    logger.info("API startup")
    logger.info("File storage: %s", settings.FILE_STORAGE)
    logger.info("Database path: %s", settings.DB_PATH)
    logger.info("Log level: %s", settings.HAAPI_LOG_LEVEL)
    
    db_create()
    yield

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)
app.include_router(system_router)
app.include_router(files_router)
app.include_router(tags_router)
app.include_router(file_tags_router)

@app.middleware("http")
async def log_request(request: Request, call_next):
    LogConsoleFormatter.method.set(request.method)
    LogConsoleFormatter.route.set(request.url.path)
    logger.info("Request received")
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    logger.debug("Hello world!")
    return {"message": "Hello World"}
