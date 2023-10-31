import asyncio
import logging
import os
from contextlib import asynccontextmanager

from concurrent_log_handler import ConcurrentRotatingFileHandler
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    unknown_exception_handler,
)
from rabbitmq.consumer import consume
from split_audio.router import router as split_audio_router


fastapi_logger = logging.getLogger("fastapi")

if not os.path.exists("logs"):
    os.mkdir("logs")
file_handler = ConcurrentRotatingFileHandler(
    "logs/system.log", "a", 10 * 1024 * 1024, 10, encoding="utf-8"
)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
)
file_handler.setFormatter(formatter)

gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
fastapi_logger.handlers = gunicorn_error_logger.handlers
gunicorn_error_logger.addHandler(file_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume())
    yield


app = FastAPI(title="Split Stereo Audio App", lifespan=lifespan)

app.include_router(split_audio_router)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unknown_exception_handler)
