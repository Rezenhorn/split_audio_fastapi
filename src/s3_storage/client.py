import aioboto3
from aiobotocore.session import ClientCreatorContext

from config import settings


def get_s3_async_session() -> aioboto3.Session:
    return aioboto3.Session(
        aws_access_key_id=settings.s3.aws_server_public_key,
        aws_secret_access_key=settings.s3.aws_server_secret_key,
        region_name="ru-central1",
    )


def get_s3_async_client(session: aioboto3.Session) -> ClientCreatorContext:
    return session.client(
        service_name="s3",
        endpoint_url=str(settings.s3.endpoint),
    )
