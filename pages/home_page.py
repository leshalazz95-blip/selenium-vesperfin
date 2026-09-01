import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    """Главная страница.

    Это образец стиля, а не готовая страница: здесь ровно столько локаторов и методов,
    сколько нужно для примеров в tests/test_navigation.py. Остальное дописываете вы.

    Правила, которых держимся:
      * локаторы — константами класса, в тестах их нет;
      * метод страницы делает одно действие и называется по действию, а не по локатору;
      * никаких assert внутри Page Object — проверки живут в utils/assertions.py.
    """

    PATH = "/"

    HEADER = (By.CSS_SELECTOR, ".header")
    LOGO_LINK = (By.CSS_SELECTOR, ".header-logo__link")

    @allure.step("Открыть главную страницу")
    def open_page(self) -> None:
        """Открывает главную страницу сайта"""
        self.open(self.PATH)

    def is_header_displayed(self) -> bool:
        """Отображается ли шапка сайта"""
        return self.is_visible(self.HEADER)

    def click_logo(self) -> None:
        """Кликает по логотипу в шапке"""
        self.click(self.LOGO_LINK)
