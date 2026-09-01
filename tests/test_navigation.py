"""Блок 1. Шапка и навигация.

Здесь реализованы два кейса из спецификации — C-01 и C-06. Это образец стиля:
остальные кейсы блока (C-02…C-05, C-07…C-10) вы дописываете в этот же файл.

Обратите внимание: в тесте нет ни одного локатора и ни одного driver.find_element.
Тест читается как сценарий, шаги видны в Allure, проверки взяты из слоя assertions.
"""

import allure
import pytest

from pages.application import Application
from utils.assertions import assert_contains, assert_equal, assert_visible

SITE_TITLE_PART = "Vesperfin"


@allure.feature("Навигация")
class TestNavigation:
    @pytest.mark.smoke
    @allure.title("C-01: открытие главной страницы")
    def test_home_page_opens(self, app: Application):
        with allure.step("Открыть главную страницу"):
            app.home_page.open_page()

        with allure.step("Проверить заголовок вкладки и шапку"):
            assert_contains(app.home_page.title, SITE_TITLE_PART, "заголовок вкладки")
            assert_visible(app.home_page.is_header_displayed(), "шапка сайта")

    @pytest.mark.smoke
    @allure.title("C-06: возврат на главную по логотипу")
    def test_logo_leads_to_home(self, app: Application):
        with allure.step("Открыть страницу контактов"):
            app.contacts_page.open_page()
            assert_visible(app.home_page.is_header_displayed(), "шапка сайта")

        with allure.step("Нажать на логотип"):
            app.home_page.click_logo()
            app.home_page.wait_url_contains(app.env_config.base_url)

        with allure.step("Проверить, что открылась главная"):
            assert_equal(
                app.home_page.current_url.rstrip("/"),
                app.env_config.base_url.rstrip("/"),
                "URL после клика по логотипу",
            )
