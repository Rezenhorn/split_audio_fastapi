from pydantic import AnyUrl, BaseModel, FilePath, HttpUrl


class StereoAudioLink(BaseModel):
    link: AnyUrl


class MonoAudioPathes(BaseModel):
    left_mono_path: FilePath
    right_mono_path: FilePath


class SuccessResponse(BaseModel):
    status: str = "success"


class MonoAudioDownloadLinks(SuccessResponse):
    left_channel_link: HttpUrl
    right_channel_link: HttpUrl
