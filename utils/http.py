"""Проверка доступности файлов, которые не нужно открывать браузером."""

import allure
import requests

from config.environments import EnvironmentConfig

TIMEOUT = 20


def resource_status(url: str, env_config: EnvironmentConfig) -> int:
    """Возвращает HTTP-статус ресурса, не скачивая его целиком."""
    with allure.step(f"Запросить ресурс {url}"):
        response = requests.get(url, timeout=env_config.timeout + TIMEOUT, stream=True)
        response.close()
        return response.status_code
