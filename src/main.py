from fastapi import FastAPI

from rmq_consumer.consumer import ThreadedConsumer
from split_audio.router import router as split_audio_router

app = FastAPI(title="Split Stereo Audio App")

app.include_router(split_audio_router)

td = ThreadedConsumer()
td.start()
