import asyncio
import os
from typing import Coroutine, Iterable

import aioboto3

from s3_storage.client import get_s3_async_client
from s3_storage.exceptions import S3UploadError


async def upload_file_to_s3(
    session: aioboto3.Session,
    bucket: str,
    path_to_file: os.PathLike,
) -> Coroutine:
    """Асинхронно загружает файл в s3 bucket."""
    object_name = os.path.basename(path_to_file)
    try:
        s3_async_client = get_s3_async_client(session)
        async with s3_async_client as s3:
            with path_to_file.open("rb") as spfp:
                await s3.upload_fileobj(spfp, bucket, object_name)
    except Exception as e:
        raise S3UploadError(str(e)) from e


async def upload_files_to_s3(
    session: aioboto3.Session, bucket: str, s3_files: Iterable[os.PathLike]
) -> asyncio.Future:
    """Асинхронно загружает несколько файлов в s3 bucket."""
    tasks = []
    for file_name in s3_files:
        tasks.append(upload_file_to_s3(session, bucket, file_name))
    await asyncio.gather(*tasks)
