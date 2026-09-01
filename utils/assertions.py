"""Общие проверки для UI-тестов.

Проверки живут отдельно от страниц: страница умеет действовать и отдавать данные,
а решать, что считать правильным, — задача этого слоя. Доменные проверки
(«цена со скидкой меньше старой») складывайте рядом со своими страницами,
по образцу API-фреймворка: pages/<раздел>/assertions.py
"""

import re

import allure


def assert_visible(is_visible: bool, element_name: str) -> None:
    """Проверяет, что элемент виден пользователю"""
    with allure.step(f"Проверка, что виден элемент: {element_name}"):
        assert is_visible, f"Элемент не отображается на странице: {element_name}"


def assert_not_visible(is_visible: bool, element_name: str) -> None:
    """Проверяет, что элемент не отображается"""
    with allure.step(f"Проверка, что элемент скрыт: {element_name}"):
        assert not is_visible, f"Элемент виден, хотя не должен: {element_name}"


def assert_equal(actual: object, expected: object, what: str) -> None:
    """Проверяет точное совпадение значения с ожидаемым"""
    with allure.step(f"Проверка {what}: ожидается {expected!r}"):
        assert actual == expected, f"{what}: ожидалось {expected!r}, получено {actual!r}"


def assert_not_equal(actual: object, forbidden: object, what: str) -> None:
    """Проверяет, что значение отличается от недопустимого"""
    with allure.step(f"Проверка {what}: значение не должно быть {forbidden!r}"):
        assert actual != forbidden, f"{what}: получено недопустимое значение {actual!r}"


def assert_contains(actual: str, expected_part: str, what: str) -> None:
    """Проверяет, что строка содержит подстроку"""
    with allure.step(f"Проверка, что {what} содержит {expected_part!r}"):
        assert expected_part in actual, f"{what}: ожидали найти {expected_part!r}, получили {actual!r}"


def assert_not_empty(value: str | None, what: str) -> None:
    """Проверяет, что значение непустое"""
    with allure.step(f"Проверка, что {what} не пустое"):
        assert value and value.strip(), f"{what} пустое, а не должно быть"


def assert_count(actual: int, expected: int, what: str) -> None:
    """Проверяет количество элементов"""
    with allure.step(f"Проверка количества ({what}): ожидается {expected}"):
        assert actual == expected, f"Количество ({what}): ожидалось {expected}, получено {actual}"


def assert_count_at_least(actual: int, minimum: int, what: str) -> None:
    """Проверяет, что элементов не меньше, чем нужно"""
    with allure.step(f"Проверка количества ({what}): не меньше {minimum}"):
        assert actual >= minimum, f"Количество ({what}): ожидалось не меньше {minimum}, получено {actual}"


def assert_in(value: str, allowed: tuple[str, ...] | list[str], what: str) -> None:
    """Проверяет, что значение содержит один из допустимых вариантов"""
    with allure.step(f"Проверка, что {what} входит в допустимый набор"):
        assert any(item in value for item in allowed), (
            f"{what}: значение {value!r} не соответствует ни одному из допустимых {allowed}"
        )


def assert_matches(value: str, pattern: str, what: str) -> None:
    """Проверяет, что значение соответствует регулярному выражению"""
    with allure.step(f"Проверка формата ({what})"):
        assert re.search(pattern, value), f"{what}: значение {value!r} не соответствует ожидаемому формату {pattern!r}"


def assert_greater(actual: float, minimum: float, what: str) -> None:
    """Проверяет, что значение больше порогового"""
    with allure.step(f"Проверка, что {what} больше {minimum}"):
        assert actual > minimum, f"{what}: ожидалось значение больше {minimum}, получено {actual}"


def assert_true(condition: bool, what: str) -> None:
    """Проверяет истинность условия"""
    with allure.step(f"Проверка: {what}"):
        assert condition, f"Не выполнено условие: {what}"


def assert_false(condition: bool, what: str) -> None:
    """Проверяет ложность условия"""
    with allure.step(f"Проверка: {what}"):
        assert not condition, f"Условие выполнено, хотя не должно: {what}"
