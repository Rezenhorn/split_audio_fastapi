from fastapi import APIRouter, Depends
from fastapi.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from split_audio.schemas import MonoAudioDownloadLinks, StereoAudioLink
from split_audio.service import add_apprequest_to_db, get_mono_audio_links

router = APIRouter(
    prefix="/split_audio",
    tags=["Split audio"]
)


@router.post("", response_model=MonoAudioDownloadLinks)
async def split_audio(
    body: StereoAudioLink,
    db_session: AsyncSession = Depends(get_async_session)
) -> MonoAudioDownloadLinks:
    link = str(body.link)
    try:
        result = get_mono_audio_links(link)
        await add_apprequest_to_db(db_session, link, True)
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        await add_apprequest_to_db(db_session, link, False)
        raise Exception from e
    return result
