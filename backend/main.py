from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
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

from .exceptions import (
    DomainException,
    FileNotFoundException,
    UnprocessableContentException,
    UnsupportedMediaTypeException,
)


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
    logger.debug("Incoming request")

    response = await call_next(request)
    logger.debug(response.status_code)

    return response


_STATUS_MAP: dict[type[DomainException], int] = {
    UnprocessableContentException: status.HTTP_422_UNPROCESSABLE_CONTENT,
    UnsupportedMediaTypeException: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    FileNotFoundException: status.HTTP_404_NOT_FOUND,
}


def _status_for(exc: DomainException) -> int:
    for cls in type(exc).__mro__:
        if cls in _STATUS_MAP:
            return _STATUS_MAP[cls]
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _log_exception(code: int, detail: str, exc: Exception) -> None:
    log_fn = logger.error if code >= 500 else logger.warning
    log_fn(f"{type(exc).__name__}: [{code}] {detail}")


@app.exception_handler(DomainException)
async def handle_domain_exception(request: Request, exc: DomainException):
    code = _status_for(exc)
    detail = str(exc)
    _log_exception(code, detail, exc)
    return JSONResponse(status_code=code, content={"detail": detail})


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    _log_exception(exc.status_code, str(exc.detail), exc)
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    _log_exception(code, str(exc), exc)
    return JSONResponse(status_code=code, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    logger.debug("Hello world!")
    return {"message": "Hello World"}
