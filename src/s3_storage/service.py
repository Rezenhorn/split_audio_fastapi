import os

from s3_storage.client import get_s3_client
from s3_storage.exceptions import S3UploadError


def upload_file_to_s3(
    path_to_file: os.PathLike, bucket: str, object_name: str | None = None
) -> None:
    """Загружает файл в s3 bucket."""
    if object_name is None:
        object_name = os.path.basename(path_to_file)
    try:
        s3_client = get_s3_client()
        s3_client.upload_file(path_to_file, bucket, object_name)
    except Exception as e:
        raise S3UploadError(str(e)) from e
