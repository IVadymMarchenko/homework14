from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
        Класс для хранения настроек приложения.

        Attributes:
        - DB_URL (str): Строка подключения к базе данных PostgreSQL.
        - SECRET_KEY_JWT (str): Секретный ключ для создания и проверки JWT токенов.
        - ALGORITHM (str): Алгоритм для создания JWT токенов (должен быть 'HS256' или 'HS512').
        - MAIL_USERNAME (EmailStr): Имя пользователя для отправки почты.
        - MAIL_PASSWORD (str): Пароль для отправки почты.
        - MAIL_FROM (str): Адрес отправителя почты.
        - MAIL_PORT (int): Порт для подключения к почтовому серверу.
        - MAIL_SERVER (str): Адрес почтового сервера.
        - REDIS_DOMAIN (str): Домен Redis.
        - REDIS_PORT (int): Порт для подключения к Redis.
        - REDIS_PASSWORD (str | None): Пароль для подключения к Redis (может быть None).
        - CLD_NAME (str): Название для работы с сервисом облачного хранения.
        - CLD_API_KEY (int): API ключ для работы с сервисом облачного хранения.
        - CLD_API_SECRET (str): Секретный ключ API для работы с сервисом облачного хранения.

        Methods:
        - validate_algorithm(cls, v: Any): Метод класса для проверки корректности алгоритма.
        """
    DB_URL: str = 'postgresql+asyncpg://postgres:567234@localhost:5432/abc'
    SECRET_KEY_JWT: str = '1234567'
    ALGORITHM: str = 'HS256'
    MAIL_USERNAME: EmailStr = 'postgres@mail.com'
    MAIL_PASSWORD: str = 'postgres'
    MAIL_FROM: str = 'postgres@fsf.com'
    MAIL_PORT: int = 567234
    MAIL_SERVER: str = 'postgres'
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = 'fastapi'
    CLD_API_KEY: int = 828841675812886
    CLD_API_SECRET: str = 'secret'

    @field_validator('ALGORITHM')
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ['HS256', 'HS512']:
            raise ValueError('algorithm must be HS256 or HS512')
        return v

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()

# class Config:
#     DB_URL = 'postgresql+asyncpg://postgres:567234@localhost:5432/postgres'
#
#
# config = Config
