"""Блок 1. Шапка и навигация.

Здесь реализованы два кейса из спецификации — C-01 и C-06. Это образец стиля:
остальные кейсы блока (C-02…C-05, C-07…C-10) вы дописываете в этот же файл.

Обратите внимание: в тесте нет ни одного локатора и ни одного driver.find_element.
Тест читается как сценарий, шаги видны в Allure, проверки взяты из слоя assertions.
"""

import allure
import pytest

from pages.application import Application
from tests.data import navigation as nav
from utils.assertions import (
    assert_contains,
    assert_count,
    assert_equal,
    assert_in,
    assert_not_empty,
    assert_not_equal,
    assert_true,
    assert_visible,
)

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
    @allure.title("C-02: состав меню в шапке")
    def test_header_menu_items(self, app: Application):
        with allure.step("Открыть главную страницу"):
            app.home_page.open_page()
            assert_visible(app.header.is_displayed(), "шапка сайта")

        with allure.step("Получить пункты меню"):
            items = app.header.get_menu_items()

        with allure.step("Сверить количество и порядок пунктов"):
            assert_count(len(items), len(nav.MENU_ITEMS), "количество пунктов меню")
            assert_equal(tuple(items), nav.MENU_ITEMS, "состав меню")

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        ("name", "path"),
        nav.MENU_LINKS,
        ids=[name for name, _ in nav.MENU_LINKS],
    )
    @allure.title("C-03: переход по пункту меню «{name}»")
    def test_menu_item_opens_page(self, app: Application, name: str, path: str):
        with allure.step("Открыть главную"):
            app.home_page.open_page()

        with allure.step(f"Кликнуть по пункту {name!r}"):
            app.header.click_menu_item(name)
            app.home_page.wait_url_contains(path)

        with allure.step("Проверить, что страница открылась"):
            assert_contains(app.home_page.current_url, path, "URL страницы")
            assert_not_empty(app.home_page.title, "заголовок вкладки")
            assert_visible(app.header.is_displayed(), "шапка сайта")

    @pytest.mark.regression
    @allure.title("C-04: «Корп. обучение» ведёт на внешний сайт")
    def test_corporate_menu_item_leads_to_external_site(self, app: Application):
        with allure.step("Открыть главную"):
            app.home_page.open_page()

        with allure.step("Получить адрес ссылки «Корп. обучение»"):
            href = app.home_page.get_attribute(app.header.CORPORATE_LINK, "href")

        with allure.step("Проверить адрес"):
            assert_not_empty(href, "адрес ссылки")
            assert_contains(href, nav.CORP_URL, "домен корпоративного сайта")

    @pytest.mark.regression
    @allure.title("C-05: «Задать вопрос» ведёт к форме вопроса")
    def test_ask_question_menu_item_leads_to_faq_form(self, app: Application):
        with allure.step("Открыть главную"):
            app.home_page.open_page()

        with allure.step("Получить адрес ссылки «Задать вопрос»"):
            href = app.home_page.get_attribute(app.header.ASK_QUESTION_LINK, "href")

        with allure.step("Проверить путь и параметр"):
            assert_not_empty(href, "адрес ссылки")
            assert_contains(href, nav.FAQ_PATH, "путь страницы вопросов")
            assert_contains(href, nav.FAQ_PARAM, "параметр перехода к форме")

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

    @pytest.mark.smoke
    @pytest.mark.parametrize("path", nav.SECTIONS, ids=nav.SECTIONS)
    @allure.title("C-07: прямое открытие раздела {path}")
    def test_section_page_opens_directly(self, app: Application, path: str):
        with allure.step(f"Открыть {path}"):
            app.home_page.open(path)

        with allure.step("Проверить, что страница загрузилась"):
            assert_contains(app.home_page.current_url, path, "URL раздела")
            assert_not_empty(app.home_page.title, "заголовок вкладки")
            assert_visible(app.header.is_displayed(), "шапка сайта")

    @pytest.mark.regression
    @allure.title("C-08: несуществующий адрес отдаёт 404")
    def test_unknown_url_returns_404_page(self, app: Application):
        with allure.step("Открыть несуществующий адрес"):
            app.home_page.open(nav.NOT_FOUND_PATH)

        with allure.step("Проверить страницу ошибки"):
            assert_not_equal(app.home_page.current_url, app.env_config.base_url, "URL")
            # Находка: сайт отдаёт title = "страница не найдена | vesperfin",
            # а не "404". Тест оставлен красным осознанно — он правильно ловит
            # расхождение.
            assert_contains(app.home_page.title.lower(), "404", "заголовок вкладки")

        with allure.step("Проверить, что шапка на месте"):
            assert_visible(app.header.is_displayed(), "шапка сайта")

    @pytest.mark.regression
    @allure.title("C-09: ссылки на соцсети в шапке")
    def test_header_social_links(self, app: Application):
        with allure.step("Открыть главную"):
            app.home_page.open_page()

        with allure.step("Собрать ссылки соцсетей"):
            hrefs = app.header.get_social_hrefs()

        with allure.step("Проверить количество и домены"):
            assert_count(len(hrefs), len(nav.SOCIAL_DOMAINS), "количество ссылок")
            for href in hrefs:
                assert_in(href, list(nav.SOCIAL_DOMAINS), "домен ссылки")

    @pytest.mark.regression
    @allure.title("C-10: кнопка возврата к началу страницы")
    def test_scroll_up_button_returns_to_top(self, app: Application):
        with allure.step("Открыть главную"):
            app.home_page.open_page()

        with allure.step("Прокрутить вниз"):
            app.home_page.scroll_to_bottom()
            assert_true(app.home_page.scroll_position() > 0, "страница прокручена")

        with allure.step("Нажать кнопку возврата наверх"):
            app.home_page.click_scroll_up()
            app.home_page.wait_scroll_to_top()

        with allure.step("Проверить, что мы в самом начале"):
            assert_equal(app.home_page.scroll_position(), 0, "позиция прокрутки")
