from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from split_audio.exceptions import DownloadError, UnsupportedExtensionError
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
    is_done = False
    try:
        result = get_mono_audio_links(link)
        is_done = True
    except (DownloadError, UnsupportedExtensionError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise Exception(str(e)) from e
    finally:
        await add_apprequest_to_db(db_session, link, is_done)
    return result
