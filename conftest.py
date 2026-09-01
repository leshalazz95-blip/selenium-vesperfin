import logging
from collections.abc import Generator

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from config.environments import Environment, EnvironmentConfig, load_environment
from pages.application import Application

logger = logging.getLogger("ui")

VIEWPORTS = {
    "mobile": (375, 812),
    "tablet": (768, 1024),
    "desktop": (1440, 900),
}


# ============================================================
#   Опции запуска
# ============================================================


def pytest_addoption(parser) -> None:
    """Опции командной строки: окружение, браузер, режим и разрешение."""
    parser.addoption(
        "--env",
        default=Environment.PROD.value,
        choices=[e.value for e in Environment],
        help="Окружение запуска",
    )
    parser.addoption("--browser", default="chrome", choices=["chrome", "firefox"], help="Браузер")
    parser.addoption("--headless", action="store_true", help="Запуск без окна браузера")
    parser.addoption(
        "--viewport",
        default="desktop",
        choices=list(VIEWPORTS),
        help="Разрешение окна: mobile / tablet / desktop",
    )


def pytest_configure(config) -> None:
    """Печатает окружение перед стартом прогона."""
    env = Environment(config.getoption("--env"))
    print(f"\nОкружение: {env}\n{load_environment(env)}\n")


# ============================================================
#   Конфигурация
# ============================================================


@pytest.fixture(scope="session")
def env(request) -> Environment:
    """Окружение из флага --env."""
    return Environment(request.config.getoption("--env"))


@pytest.fixture(scope="session")
def env_config(env: Environment) -> EnvironmentConfig:
    """Конфиг окружения: базовый URL и таймаут ожиданий."""
    return load_environment(env)


# ============================================================
#   Браузер
# ============================================================


def _create_driver(browser: str, headless: bool, width: int, height: int) -> WebDriver:
    """Создаёт драйвер запрошенного браузера."""
    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--disable-dev-shm-usage")
        # включаем сбор логов консоли — они пригодятся при разборе падений
        options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        return webdriver.Chrome(options=options)

    options = FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(width, height)
    return driver


@pytest.fixture
def driver(request, env_config: EnvironmentConfig) -> Generator[WebDriver, None, None]:
    """Свежий браузер на каждый тест: чистый профиль, никакого протекания состояния."""
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    width, height = VIEWPORTS[request.config.getoption("--viewport")]

    driver = _create_driver(browser, headless, width, height)
    driver.set_page_load_timeout(60)

    yield driver

    driver.quit()


@pytest.fixture
def mobile_viewport(request) -> None:
    """Требует запуска с мобильным разрешением окна.

    Тесты мобильной версии на десктопном разрешении не имеют смысла: кнопки меню там нет.
    Лучше пропустить их с внятной причиной, чем получить непонятное падение.
    """
    if request.config.getoption("--viewport") != "mobile":
        pytest.skip("Тест мобильной версии: запускайте с ключом --viewport=mobile")


@pytest.fixture
def app(driver: WebDriver, env_config: EnvironmentConfig) -> Application:
    """Точка входа ко всем страницам приложения."""
    return Application(driver, env_config)


# ============================================================
#   Отчётность
# ============================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """При падении теста кладёт в Allure скриншот, URL и логи консоли браузера."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(driver.current_url, name="url", attachment_type=allure.attachment_type.TEXT)
        if driver.capabilities.get("browserName") == "chrome":
            console = "\n".join(f"{entry['level']}: {entry['message']}" for entry in driver.get_log("browser"))
            allure.attach(console or "пусто", name="browser console", attachment_type=allure.attachment_type.TEXT)
    except Exception as error:
        logger.warning("Не удалось собрать артефакты падения: %s", error)
