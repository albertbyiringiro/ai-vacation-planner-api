from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    env: Literal["development", "staging", "production"] = "development"
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    database_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


SettingsDep = Annotated[Settings, Depends(get_settings)]
