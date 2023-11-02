from pathlib import Path

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent


class DbSettings(BaseSettings):
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")
    password: str = Field(alias="POSTGRES_PASSWORD")
    user: str = Field(alias="POSTGRES_USER")
    name: str = Field(alias="POSTGRES_DB")

    model_config = SettingsConfigDict(env_file="src/.env", extra="ignore")


class RmqSettings(BaseSettings):
    host: str = Field(alias="RMQ_HOST")
    port: int = Field(alias="RMQ_PORT")
    user: str = Field(alias="RABBITMQ_DEFAULT_USER")
    password: str = Field(alias="RABBITMQ_DEFAULT_PASS")
    vhost: str = Field(alias="RMQ_VHOST")

    tasks_queue: str = "tasks"
    results_queue: str = "result"

    model_config = SettingsConfigDict(env_file="src/.env", extra="ignore")


class S3Settings(BaseSettings):
    endpoint: AnyUrl = Field(alias="S3_ENDPOINT")
    bucket: str
    aws_server_public_key: str
    aws_server_secret_key: str

    model_config = SettingsConfigDict(env_file="src/.env", extra="ignore")


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    rmq: RmqSettings = RmqSettings()
    s3: S3Settings = S3Settings()

    path_to_temp_files: Path = Path(BASE_DIR) / "temp"
    supported_extensions: list[str] = [
        "aac",
        "mid",
        "mp3",
        "m4a",
        "flac",
        "wav",
        "wmv",
        "aiff",
        "alac",
        "m4r",
    ]

    model_config = SettingsConfigDict(env_file="src/.env", extra="ignore")


settings = Settings()
