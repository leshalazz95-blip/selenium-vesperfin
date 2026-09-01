from enum import StrEnum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Список поддерживаемых окружений для запуска тестов.

    Сейчас окружение одно — боевой сайт. Когда появится тестовый стенд,
    добавьте его сюда и положите рядом файл config/.env.<название>.
    """

    PROD = "prod"

    def __str__(self) -> str:
        """Название окружения с заглавной буквы для логов и отчётов"""
        return self.value.capitalize()


class EnvironmentConfig(BaseSettings):
    """Конфиг окружения. Значения подтягиваются из config/.env.* или переменных окружения."""

    base_url: str = Field(default="https://vesperfin.com")
    timeout: int = Field(default=10)

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
        case_sensitive=False,
    )

    def url(self, path: str = "/") -> str:
        """Собирает абсолютный URL из базового адреса и пути"""
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def __str__(self) -> str:
        """Краткое представление конфига для логов"""
        return f"- Vesperfin UI: {self.base_url}"


def load_environment(env: Environment | str) -> EnvironmentConfig:
    """Возвращает конфиг запрошенного окружения. Значения берутся из config/.env.{env}"""
    env = env if isinstance(env, Environment) else Environment(env.lower())
    env_file_path = Path(__file__).parent / f".env.{env.value}"

    return EnvironmentConfig(_env_file=str(env_file_path))
