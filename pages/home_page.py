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
    SCROLL_UP_BUTTON = (By.CSS_SELECTOR, "[data-scroll-to-top]")
    # Кнопка «вверх» рендерится динамически и не всегда есть в DOM.
    # Стабильный селектор — обёртка с data-атрибутом; клик по ней
    # срабатывает через делегирование событий.

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

    def click_scroll_up(self) -> None:
        """Кликает по кнопке возврата к началу страницы"""
        self.scroll_to(self.SCROLL_UP_BUTTON)
        self.click(self.SCROLL_UP_BUTTON)
