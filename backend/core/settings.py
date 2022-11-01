from functools import cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Messenger"
    descriprion: str = "Awesome async messenger"
    redis_host: str = "localhost"
    redis_port: int = 6379
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_name: str = "messenger"
    api_prefix: str = "/api"
    secret: str

    class Config:
        env_file = "dev.env"


@cache
def get_settings(**kwargs):
    return Settings(**kwargs)
