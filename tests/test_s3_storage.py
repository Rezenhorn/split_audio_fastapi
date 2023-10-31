from src.config import settings
from src.s3_storage.service import upload_file_to_s3, upload_files_to_s3


async def test_upload_file_to_s3(
    s3_async_session,
    test_bucket,
    path_to_test_audio,
):
    await upload_file_to_s3(s3_async_session, test_bucket, path_to_test_audio)
    async with s3_async_session.resource(
        "s3", endpoint_url=str(settings.s3_endpoint)
    ) as s3:
        bucket = await s3.Bucket(test_bucket)
        counter = 0
        async for obj in bucket.objects.filter(Prefix="test_audio.wav"):
            assert obj.key == "test_audio.wav"
            counter += 1
        assert counter == 1


async def test_upload_files_to_s3(
    path_to_test_audio, path_to_test_picture, s3_async_session, test_bucket
):
    await upload_files_to_s3(
        s3_async_session,
        test_bucket,
        [path_to_test_audio, path_to_test_picture],
    )
    async with s3_async_session.resource(
        "s3", endpoint_url=str(settings.s3_endpoint)
    ) as s3:
        bucket = await s3.Bucket(test_bucket)
        counter = 0
        async for obj in bucket.objects.filter(Prefix="test_"):
            assert obj.key in ("test_audio.wav", "test_pic.jpg")
            counter += 1
        assert counter == 2
