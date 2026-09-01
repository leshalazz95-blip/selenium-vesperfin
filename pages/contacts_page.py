import allure

from pages.base_page import BasePage


class ContactsPage(BasePage):
    """Страница контактов. Форма обратной связи здесь та же, что на главной,
    но с дополнительным полем сообщения."""

    PATH = "/contacts/"

    @allure.step("Открыть страницу контактов")
    def open_page(self) -> None:
        """Открывает страницу контактов"""
        self.open(self.PATH)
