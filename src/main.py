import logging

from fastapi import FastAPI

from rmq_consumer.consumer import ThreadedConsumer
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

td = ThreadedConsumer()
td.start()
