import json

from aio_pika import connect, IncomingMessage, Message
from aio_pika.channel import AbstractChannel
from aiormq.exceptions import AMQPConnectionError
from fastapi.logger import logger

from config import settings
from split_audio.service import get_mono_audio_links


RMQ_URL = (
    f"amqp://{settings.rmq.user}:{settings.rmq.password}"
    f"@{settings.rmq.host}:{settings.rmq.port}/{settings.rmq.vhost}"
)


async def process_message(channel: AbstractChannel, message: IncomingMessage):
    async with message.process():
        link: str = json.loads(message.body).get("link")
        if link:
            mono_files_links = await get_mono_audio_links(link)
            message: str = json.dumps(
                mono_files_links.model_dump(mode="json"), ensure_ascii=False
            )
            logger.info(f"Отправляем результат в RMQ: {link}")
            await channel.default_exchange.publish(
                Message(message.encode(), content_type="application/json"),
                routing_key=settings.rmq.results_queue,
            )
        else:
            logger.error("Сообщение в RMQ не содержит `link`.")


async def rmq_consume():
    try:
        connection = await connect(RMQ_URL)
    except AMQPConnectionError as error:
        logger.error(f"Ошибка присоединения к RabbitMQ: {error}")
        raise AMQPConnectionError from error
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=3)
    tasks_queue = await channel.declare_queue(
        settings.rmq.tasks_queue, durable=True
    )
    await channel.declare_queue(settings.rmq.results_queue, durable=True)
    async with tasks_queue.iterator() as queue_iter:
        async for message in queue_iter:
            try:
                await process_message(channel, message)
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения: {e}")
