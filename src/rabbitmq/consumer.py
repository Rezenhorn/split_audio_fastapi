import json

from aio_pika import connect, IncomingMessage, Message
from aio_pika.channel import AbstractChannel
from aiormq.exceptions import AMQPConnectionError
from fastapi.logger import logger

from config import settings
from split_audio.service import get_mono_audio_links


RMQ_URL = (
    f"amqp://{settings.rmq_user}:{settings.rmq_pass}"
    f"@{settings.rmq_host}:{settings.rmq_port}/{settings.rmq_vhost}"
)


async def process_message(channel: AbstractChannel, message: IncomingMessage):
    async with message.process():
        link: str = json.loads(message.body).get("link")
        if link:
            mono_files_links = await get_mono_audio_links(link)
            message: str = json.dumps(
                mono_files_links.model_dump(mode="json"),
                ensure_ascii=False
            )
            logger.info(f"Отправляем результат в RMQ: {link}")
            await channel.default_exchange.publish(
                Message(message.encode()),
                routing_key=settings.rmq_results_queue,
            )
        else:
            logger.error("Сообщение в RMQ не содержит `link`.")


async def consume():
    try:
        connection = await connect(RMQ_URL)
    except AMQPConnectionError as error:
        logger.error(f"Ошибка присоединения к RabbitMQ: {error}")
        raise AMQPConnectionError from error
    channel = await connection.channel()
    tasks_queue = await channel.declare_queue(
        settings.rmq_tasks_queue, durable=True
    )
    await channel.declare_queue(
        settings.rmq_results_queue, durable=True
    )
    async with tasks_queue.iterator() as queue_iter:
        async for message in queue_iter:
            await process_message(channel, message)
