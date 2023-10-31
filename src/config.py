from pathlib import Path

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    db_host: str = Field(alias='POSTGRES_HOST')
    db_port: int = Field(alias='POSTGRES_PORT')
    db_pass: str = Field(alias='POSTGRES_PASSWORD')
    db_user: str = Field(alias='POSTGRES_USER')
    db_name: str = Field(alias='POSTGRES_DB')

    pgadmin_default_email: str
    pgadmin_default_password: str
    pgadmin_listen_port: int

    rmq_host: str
    rmq_port: int
    rmq_user: str = Field(alias='RABBITMQ_DEFAULT_USER')
    rmq_pass: str = Field(alias='RABBITMQ_DEFAULT_PASS')
    rmq_vhost: str

    rmq_tasks_queue: str = "tasks"
    rmq_results_queue: str = "result"

    s3_endpoint: AnyUrl
    bucket: str
    aws_server_public_key: str
    aws_server_secret_key: str

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
        "m4r"
    ]

    model_config = SettingsConfigDict(env_file="src/.env")


settings = Settings()
