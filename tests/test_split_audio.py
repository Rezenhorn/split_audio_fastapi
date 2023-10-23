import os

import pytest

from src.split_audio.service import download_file, split_audio


@pytest.mark.parametrize(
    "url, file_name",
    [
        ("https://storage.yandexcloud.net/rezenhorn-bucket/M1F1-Alaw-AFsp.wav",
         "test_wav"),
        ("https://storage.yandexcloud.net/rezenhorn-bucket/test.svg",
         "test_img"),
    ]
)
def test_download_file(url, file_name):
    path_to_file = download_file(url, file_name)
    assert isinstance(path_to_file, os.PathLike)
    assert os.path.isfile(path_to_file)


def test_download_fail():
    with pytest.raises(Exception) as excinfo:
        download_file("https://example.com", "test_1")
    assert "Проверьте переданную ссылку" in str(excinfo.value)


def test_split_audio(path_to_test_audio):
    mono_audio_pathes = split_audio(path_to_test_audio)
    assert isinstance(mono_audio_pathes.left_mono_path, os.PathLike)
    assert isinstance(mono_audio_pathes.right_mono_path, os.PathLike)
    assert os.path.isfile(mono_audio_pathes.left_mono_path)
    assert os.path.isfile(mono_audio_pathes.right_mono_path)
    _, left_extension = os.path.splitext(mono_audio_pathes.left_mono_path)
    _, right_extension = os.path.splitext(mono_audio_pathes.right_mono_path)
    assert left_extension == ".wav"
    assert right_extension == ".wav"
