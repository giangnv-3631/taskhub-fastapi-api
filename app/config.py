from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    MAIL_FROM_DEFAULT,
    SECRET_KEY_MIN_LENGTH,
    SMTP_DEFAULT_PORT,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    secret_key: str = Field(min_length=SECRET_KEY_MIN_LENGTH)
    algorithm: str = JWT_ALGORITHM
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
    smtp_host: str = ""
    smtp_port: int = SMTP_DEFAULT_PORT
    mail_from: str = MAIL_FROM_DEFAULT


settings = Settings()
