import asyncio
import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    unknown_exception_handler
)
from rabbitmq.consumer import consume
from split_audio.router import router as split_audio_router


logger = logging.getLogger("fastapi")
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename='./server.log')
formatter = logging.Formatter(
    "[%(asctime)s][%(levelname)s]: %(module)s - line:%(lineno)d - %(message)s"
)
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


app = FastAPI(title="Split Stereo Audio App")

app.include_router(split_audio_router)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unknown_exception_handler)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume())
