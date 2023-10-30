import asyncio
import os
import shutil
from pathlib import Path
from typing import AsyncGenerator
from unittest import mock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src import Base
from src.config import settings
from src.main import app
from src.s3_storage.client import get_s3_async_session


DATABASE_URL_TEST = (
    f"postgresql+asyncpg://"
    f"{settings.db_user}:{settings.db_pass}"
    f"@{settings.db_host}:{settings.db_port}"
    f"/{settings.db_name}"
)

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    assert settings.db_name == "test_db"
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


current_file = os.path.realpath(__file__)
current_directory = os.path.dirname(current_file)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def change_temp_files_path():
    path_to_temp_files = Path(current_directory) / "temp"
    if not os.path.exists(path_to_temp_files):
        os.mkdir(f"{current_directory}/temp")
    with mock.patch(
        "config.settings.path_to_temp_files",
        new=path_to_temp_files
    ):
        yield
        shutil.rmtree(path_to_temp_files)


@pytest.fixture(scope="session")
def path_to_test_audio():
    return Path(current_directory) / "test_data/test_audio.wav"


@pytest.fixture(scope="session")
def path_to_test_picture():
    return Path(current_directory) / "test_data/test_pic.jpg"


@pytest.fixture(scope="session")
def test_bucket():
    return "rezenhorn-test-bucket"


@pytest.fixture(scope="session")
async def s3_async_session():
    return get_s3_async_session()


@pytest.fixture(scope="session", autouse=True)
async def clean_test_bucket(s3_async_session, test_bucket):
    async with s3_async_session.resource(
        "s3", endpoint_url=str(settings.s3_endpoint)
    ) as s3:
        bucket = await s3.Bucket(test_bucket)
        async for obj in bucket.objects.all():
            await obj.delete()
    yield s3_async_session
    async with s3_async_session.resource(
        "s3", endpoint_url=str(settings.s3_endpoint)
    ) as s3:
        bucket = await s3.Bucket(test_bucket)
        async for obj in bucket.objects.all():
            await obj.delete()
