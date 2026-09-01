from selenium.webdriver.remote.webdriver import WebDriver

from config.environments import EnvironmentConfig
from pages.contacts_page import ContactsPage
from pages.home_page import HomePage


class Application:
    """Фасад приложения: единая точка входа ко всем страницам и общим компонентам.

    В тест приходит один объект `app`, а не пачка фикстур на каждую страницу.
    Добавили новую страницу или компонент — зарегистрировали здесь одной строкой.
    """

    def __init__(self, driver: WebDriver, env_config: EnvironmentConfig) -> None:
        self.driver = driver
        self.env_config = env_config

        self.home_page = HomePage(driver, env_config)
        self.contacts_page = ContactsPage(driver, env_config)

        # Сюда добавляете свои страницы и сквозные компоненты, например:
        # self.courses_page = CoursesPage(driver, env_config)
        # self.course_page = CoursePage(driver, env_config)
        # self.faq_page = FaqPage(driver, env_config)
        # self.header = Header(driver, env_config)
        # self.footer = Footer(driver, env_config)
        # self.cookie_banner = CookieBanner(driver, env_config)
        # self.feedback_form = FeedbackForm(driver, env_config)
