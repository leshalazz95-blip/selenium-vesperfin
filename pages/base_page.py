import logging

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.environments import EnvironmentConfig

logger = logging.getLogger("ui")

Locator = tuple[str, str]


class BasePage:
    """Базовая страница: ожидания, действия и вложения в Allure.

    Наследники описывают локаторы и доменные методы, но НЕ работают с self.driver напрямую —
    всё взаимодействие идёт через методы этого класса.
    """

    def __init__(self, driver: WebDriver, env_config: EnvironmentConfig) -> None:
        self.driver = driver
        self.env_config = env_config
        self.timeout = env_config.timeout
        self.wait = WebDriverWait(driver, self.timeout)

    # ------------------------------------------------------------------
    # Навигация
    # ------------------------------------------------------------------

    def open(self, path: str = "/") -> None:
        """Открывает страницу. Принимает путь относительно base_url или абсолютный адрес."""
        url = path if path.startswith("http") else self.env_config.url(path)
        with allure.step(f"Открыть {url}"):
            logger.info("open url=%s", url)
            self.driver.get(url)

    @property
    def current_url(self) -> str:
        """Текущий URL страницы"""
        return self.driver.current_url

    @property
    def title(self) -> str:
        """Заголовок вкладки"""
        return self.driver.title

    # ------------------------------------------------------------------
    # Поиск и ожидания
    # ------------------------------------------------------------------

    def find(self, locator: Locator, timeout: int | None = None) -> WebElement:
        """Ждёт появления элемента в DOM и возвращает его"""
        return self._wait(timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Элемент {locator} не появился в DOM за {timeout or self.timeout} сек",
        )

    def find_visible(self, locator: Locator, timeout: int | None = None) -> WebElement:
        """Ждёт, пока элемент станет видимым, и возвращает его"""
        return self._wait(timeout).until(
            EC.visibility_of_element_located(locator),
            message=f"Элемент {locator} не стал видимым за {timeout or self.timeout} сек",
        )

    def find_all(self, locator: Locator, timeout: int | None = None) -> list[WebElement]:
        """Ждёт появления хотя бы одного элемента и возвращает все найденные"""
        return self._wait(timeout).until(
            EC.presence_of_all_elements_located(locator),
            message=f"Элементы {locator} не появились за {timeout or self.timeout} сек",
        )

    def is_visible(self, locator: Locator, timeout: int | None = None) -> bool:
        """Видим ли элемент. Не бросает исключение — возвращает False по таймауту"""
        try:
            self.find_visible(locator, timeout)
        except TimeoutException:
            return False
        return True

    def wait_invisible(self, locator: Locator, timeout: int | None = None) -> None:
        """Ждёт, пока элемент исчезнет со страницы"""
        self._wait(timeout).until(
            EC.invisibility_of_element_located(locator),
            message=f"Элемент {locator} остался видимым спустя {timeout or self.timeout} сек",
        )

    def wait_url_contains(self, part: str, timeout: int | None = None) -> None:
        """Ждёт, пока URL страницы начнёт содержать подстроку"""
        self._wait(timeout).until(
            EC.url_contains(part),
            message=f"URL не содержит {part!r}. Текущий URL: {self.driver.current_url}",
        )

    def _wait(self, timeout: int | None) -> WebDriverWait:
        """Возвращает ожидание с нужным таймаутом"""
        return WebDriverWait(self.driver, timeout) if timeout else self.wait

    # ------------------------------------------------------------------
    # Действия
    # ------------------------------------------------------------------

    def click(self, locator: Locator, timeout: int | None = None) -> None:
        """Ждёт кликабельности элемента и кликает по нему"""
        with allure.step(f"Клик по {locator}"):
            element = self._wait(timeout).until(
                EC.element_to_be_clickable(locator),
                message=f"Элемент {locator} не стал кликабельным за {timeout or self.timeout} сек",
            )
            logger.info("click locator=%s", locator)
            element.click()

    def fill(self, locator: Locator, text: str) -> None:
        """Очищает поле и вводит текст"""
        with allure.step(f"Ввести {text!r} в {locator}"):
            element = self.find_visible(locator)
            element.clear()
            element.send_keys(text)

    def get_text(self, locator: Locator) -> str:
        """Текст элемента без лишних пробелов"""
        return self.find_visible(locator).text.strip()

    def get_texts(self, locator: Locator) -> list[str]:
        """Тексты всех найденных элементов"""
        return [element.text.strip() for element in self.find_all(locator)]

    def get_attribute(self, locator: Locator, name: str) -> str | None:
        """Значение атрибута элемента"""
        return self.find(locator).get_attribute(name)

    def get_attributes(self, locator: Locator, name: str) -> list[str | None]:
        """Значения атрибута у всех найденных элементов"""
        return [element.get_attribute(name) for element in self.find_all(locator)]

    def count(self, locator: Locator) -> int:
        """Количество элементов на странице (без ожидания появления)"""
        return len(self.driver.find_elements(*locator))

    def is_selected(self, locator: Locator) -> bool:
        """Отмечен ли чекбокс или радиокнопка"""
        return self.find(locator).is_selected()

    def is_valid(self, locator: Locator) -> bool:
        """Проходит ли поле браузерную валидацию формы"""
        return self.driver.execute_script("return arguments[0].checkValidity();", self.find(locator))

    def validation_message(self, locator: Locator) -> str:
        """Текст браузерного сообщения о невалидности поля"""
        return self.driver.execute_script("return arguments[0].validationMessage;", self.find(locator))

    def is_in_viewport(self, locator: Locator) -> bool:
        """Находится ли элемент в видимой области окна"""
        return self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            const height = window.innerHeight || document.documentElement.clientHeight;
            return rect.top < height && rect.bottom > 0;
            """,
            self.find(locator),
        )

    def meta_content(self, selector: str) -> str | None:
        """Содержимое мета-тега по CSS-селектору (тег может быть скрыт, поэтому читаем из DOM)"""
        return self.driver.execute_script(
            "const el = document.querySelector(arguments[0]); return el ? el.getAttribute('content') : null;",
            selector,
        )

    def link_href(self, selector: str) -> str | None:
        """Адрес ссылки по CSS-селектору"""
        return self.driver.execute_script(
            "const el = document.querySelector(arguments[0]); return el ? el.getAttribute('href') : null;",
            selector,
        )

    def scroll_to(self, locator: Locator) -> None:
        """Прокручивает страницу к элементу"""
        with allure.step(f"Прокрутить к {locator}"):
            element = self.find(locator)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    # ------------------------------------------------------------------
    # Состояние браузера
    # ------------------------------------------------------------------

    def local_storage_item(self, key: str) -> str | None:
        """Значение ключа из localStorage"""
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def clear_storage(self) -> None:
        """Чистит localStorage, sessionStorage и куки"""
        with allure.step("Очистить хранилище браузера"):
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
            self.driver.delete_all_cookies()

    def scroll_position(self) -> int:
        """Текущая вертикальная прокрутка страницы в пикселях"""
        return self.driver.execute_script("return Math.round(window.pageYOffset);")

    def scroll_to_bottom(self) -> None:
        """Прокручивает страницу в самый конец"""
        with allure.step("Прокрутить страницу вниз"):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def wait_scroll_to_top(self, timeout: int | None = None) -> None:
        """Ждёт, пока страница окажется в самом начале (прокрутка анимированная)"""
        self._wait(timeout).until(
            lambda _: self.scroll_position() == 0,
            message=f"Страница не вернулась в начало за {timeout or self.timeout} сек",
        )

    def reload(self) -> None:
        """Перезагружает текущую страницу"""
        with allure.step("Перезагрузить страницу"):
            self.driver.refresh()

    # ------------------------------------------------------------------
    # Отчётность
    # ------------------------------------------------------------------

    def attach_screenshot(self, name: str = "screenshot") -> None:
        """Прикрепляет скриншот страницы к Allure-отчёту"""
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
