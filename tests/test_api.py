from unittest import mock

from httpx import AsyncClient
from sqlalchemy import select
# from src.models import AppRequest


async def test_split_audio_api(ac: AsyncClient, test_bucket):
    with mock.patch("config.settings.bucket", new=test_bucket):

        link = "https://storage.yandexcloud.net/rezenhorn-bucket/M1F1-Alaw-AFsp.wav"
        response = await ac.post("/split_audio", json={"link": link})
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert isinstance(response.json()["left_channel_link"], str)
        assert isinstance(response.json()["right_channel_link"], str)
        #
        #     query = select(AppRequest).where(
        #         AppRequest.link == link and AppRequest.is_done is True
        #     )
        #     result = await session.execute(query)
        #     assert len(result) == 1
