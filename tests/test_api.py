from unittest import mock

from httpx import AsyncClient
from sqlalchemy import select

from src.models import AppRequest
from conftest import async_session_maker


async def test_split_audio_api(ac: AsyncClient, test_bucket: str):
    with mock.patch("config.settings.bucket", new=test_bucket):
        link = "https://storage.yandexcloud.net/rezenhorn-bucket/M1F1-Alaw-AFsp.wav"
        response = await ac.post("/split_audio", json={"link": link})
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert isinstance(response.json()["left_channel_link"], str)
        assert isinstance(response.json()["right_channel_link"], str)
        async with async_session_maker() as session:
            query = select(AppRequest).where(
                AppRequest.link == link,
                AppRequest.is_done == True,  # noqa: E712
            )
            result = await session.execute(query)
            assert len(result.all()) == 1
