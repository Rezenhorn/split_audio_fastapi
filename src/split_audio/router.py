from fastapi import APIRouter

from split_audio.schemas import MonoAudioDownloadLinks, StereoAudioLink
from split_audio.service import get_mono_audio_links

router = APIRouter(
    prefix="/split_audio",
    tags=["Split audio"]
)


@router.post("", response_model=MonoAudioDownloadLinks)
def split_audio(link: StereoAudioLink) -> MonoAudioDownloadLinks:
    result = get_mono_audio_links(str(link.link))
    return result
