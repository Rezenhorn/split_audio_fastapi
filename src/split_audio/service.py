import os
import urllib.request
import uuid

import filetype
from pydub import AudioSegment

from config import settings
from s3_storage.service import upload_file_to_s3
from split_audio.exceptions import DownloadError, UnsupportedExtensionError
from split_audio.schemas import MonoAudioDownloadLinks, MonoAudioPathes


def split_audio(path_to_file: os.PathLike) -> MonoAudioPathes:
    """
    Разбивает стерео аудио-файл на 2 файла по каналам.
    Возвращает пути к полученным файлам и удаляет исходный файл.
    """
    stereo_audio = AudioSegment.from_file(path_to_file)
    file_name = os.path.basename(path_to_file)
    mono_audios = stereo_audio.split_to_mono()
    path_to_left_channel = (
        settings.path_to_temp_files / f"mono_left_{file_name}"
    )
    path_to_right_channel = (
        settings.path_to_temp_files / f"mono_right_{file_name}"
    )
    mono_audios[0].export(path_to_left_channel)
    mono_audios[1].export(path_to_right_channel)
    os.remove(path_to_file)
    return MonoAudioPathes(
        left_mono_path=path_to_left_channel,
        right_mono_path=path_to_right_channel
    )


def download_file(url: str, file_name: str) -> os.PathLike:
    """Загружает файл по ссылке и возвращает путь до него."""
    path_to_file, _ = urllib.request.urlretrieve(
        url, settings.path_to_temp_files / file_name
    )
    return _rename_file_with_extension(path_to_file)


def _rename_file_with_extension(path_to_file: str) -> os.PathLike:
    """Определяет расширение файла и добавляет его в его название."""
    file_name = os.path.basename(path_to_file)
    try:
        file_extension = filetype.guess(path_to_file).extension
    except AttributeError as e:
        raise DownloadError(
            "Ошибка определения расширения файла. Проверьте переданную ссылку."
        ) from e
    file_name_with_extension = f"{file_name}.{file_extension}"
    path_to_file_with_extension = (
        settings.path_to_temp_files / file_name_with_extension
    )
    os.rename(path_to_file, path_to_file_with_extension)
    return path_to_file_with_extension


def get_mono_audio_links(link: str) -> MonoAudioDownloadLinks:
    """
    Разбивает переданный по ссылке стерео
    аудиофайл на 2 по каналам и загружает в s3 хранилище.
    Возвращает ссылки на скачивание полученных файлов.
    """
    file_name = str(uuid.uuid4())
    path_to_file = download_file(link, file_name)
    if ((extension := str(path_to_file).split(".")[-1])
            not in settings.supported_extensions):
        os.remove(path_to_file)
        raise UnsupportedExtensionError(
            f"Расширение файла `{extension}` не поддерживается."
        )
    paths_to_files: MonoAudioPathes = split_audio(path_to_file)
    try:
        upload_file_to_s3(
            paths_to_files.left_mono_path, settings.bucket
        )
        upload_file_to_s3(
            paths_to_files.right_mono_path, settings.bucket
        )
    finally:
        os.remove(paths_to_files.left_mono_path)
        os.remove(paths_to_files.right_mono_path)
    left_channel_link = (f"{settings.s3_endpoint}"
                         f"{settings.bucket}/"
                         f"{os.path.basename(paths_to_files.left_mono_path)}")
    right_channel_link = (f"{settings.s3_endpoint}"
                          f"{settings.bucket}/"
                          f"{os.path.basename(paths_to_files.right_mono_path)}")
    return MonoAudioDownloadLinks(
        left_channel_link=left_channel_link,
        right_channel_link=right_channel_link
    )