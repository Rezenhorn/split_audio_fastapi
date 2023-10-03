import boto3

from config import settings


def get_s3_client():
    session = boto3.Session(
        aws_access_key_id=settings.aws_server_public_key,
        aws_secret_access_key=settings.aws_server_secret_key,
        region_name="ru-central1"
    )
    s3_client = session.client(
        service_name="s3",
        endpoint_url=str(settings.s3_endpoint),
    )
    return s3_client
