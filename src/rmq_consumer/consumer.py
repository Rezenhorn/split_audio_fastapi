import json
import threading

import pika
from fastapi.logger import logger

from config import settings
from split_audio.service import get_mono_audio_links


class ThreadedConsumerBase(threading.Thread):
    """Базовый класс для получения и обработки сообщений из RMQ."""

    def __init__(self):
        threading.Thread.__init__(self)
        self.rmq_url = (
            f"amqp://{settings.rmq_user}:{settings.rmq_pass}"
            f"@{settings.rmq_host}:{settings.rmq_port}/{settings.rmq_vhost}"
        )
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rmq_url)
            )
            self.channel = self.connection.channel()
        except pika.exceptions.AMQPConnectionError as error:
            logger.error(f"Ошибка присоединения к RabbitMQ: {error}")
            raise pika.exceptions.AMQPConnectionError from error

    def handle_messages(self, data):
        """Обрабатывает сообщение из очереди RabbitMQ."""
        ...

    def callback(self, channel, method, properties, body):
        """Обрабатывает каждое полученное сообщение."""
        try:
            data = json.loads(body)
            logger.info(f"Получено сообщение в RMQ: {data}")
            self.handle_messages(data)
        except Exception as e:
            logger.error(f"Ошибка в консьюмере: {e}")
        finally:
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        """Прослушивание очереди."""
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Останавливает чтение сообщений консьюмером."""
        self.channel.stop_consuming()
        self.connection.close()


class ThreadedConsumer(ThreadedConsumerBase):
    """
    Поток, читающий сообщения из очереди `tasks`.
    Для каждого сообщения вызывается функцию обработки.
    """

    def __init__(self):
        super().__init__()
        self.channel.queue_declare(
            queue=settings.rmq_tasks_queue, durable=True
        )
        self.channel.queue_declare(
            queue=settings.rmq_results_queue, durable=True
        )
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=settings.rmq_tasks_queue,
            on_message_callback=self.callback
        )

    def handle_messages(self, data: dict) -> None:
        """Обрабатывает сообщение из очереди RabbitMQ."""
        link: str = data.get("link")
        if link:
            mono_files_links = get_mono_audio_links(link)
            logger.info(f"Отправляем результат в RMQ: {data}")
            self.channel.basic_publish(
                exchange="",
                routing_key=settings.rmq_results_queue,
                body=json.dumps(
                    mono_files_links.model_dump(mode="json"),
                    ensure_ascii=False
                )
            )
        else:
            logger.error("Сообщение в RMQ не содержит `link`.")
