from allure import step
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class Header(BasePage):
    """Шапка сайта."""

    HEADER = (By.CSS_SELECTOR, "header.header")
    LOGO_LINK = (By.CSS_SELECTOR, ".header-logo__link")

    MENU_LINKS = (By.CSS_SELECTOR, ".header-menu-nav > .header-menu-nav__link")

    CORPORATE_LINK = (
        By.XPATH,
        "//a[contains(@class, 'header-menu-nav__link')][.//span[text()='Корп. обучение']]",
    )
    ASK_QUESTION_LINK = (
        By.XPATH,
        "//a[contains(@class, 'header-menu-nav__link')][contains(., 'Задать вопрос')]",
    )

    SOCIAL_LINKS = (By.CSS_SELECTOR, ".header-menu-social__link__ico")

    def is_displayed(self) -> bool:
        return self.is_visible(self.HEADER)

    def get_menu_items(self) -> list[str]:
        # textContent, а не .text: у «Главной» видимый текст пуст (скрыта стилями),
        # а у «Корп. обучение» внутри два span — нужны оба
        items = self.find_all(self.MENU_LINKS)
        return [" ".join(el.get_attribute("textContent").split()) for el in items]

    def get_social_hrefs(self) -> list[str]:
        return [href for href in self.get_attributes(self.SOCIAL_LINKS, "href") if href]

    @step("Клик по пункту меню: {name!r}")
    def click_menu_item(self, name: str) -> None:
        # normalize-space — потому что в HTML переносы строк и отступы
        locator = (
            By.XPATH,
            f"//a[contains(@class, 'header-menu-nav__link')][normalize-space(.)='{name}']",
        )
        self.click(locator)

    def click_logo(self) -> None:
        self.click(self.LOGO_LINK)
