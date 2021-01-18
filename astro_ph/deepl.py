__all__ = ["Driver", "Language", "translate"]


# standard library
from enum import auto, Enum
from typing import Tuple, Union
from urllib.parse import quote


# third-party packages
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver import Edge, Safari
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait
from typing_extensions import Final


# constants
TIMEOUT: Final[int] = 30
TRANSLATION_CLASS: Final[str] = "lmt__translations_as_text__text_btn"
TRANSLATOR_URL: Final[str] = "https://www.deepl.com/translator"


class Driver(Enum):
    """Available webdrivers for translation."""

    CHROME = auto()
    EDGE = auto()
    FIREFOX = auto()
    SAFARI = auto()


class Language(Enum):
    """Available languages for translation."""

    AUTO = auto()
    DE = auto()
    EN = auto()
    FR = auto()
    IT = auto()
    JA = auto()
    ES = auto()
    NL = auto()
    PL = auto()
    PT = auto()
    RU = auto()
    ZH = auto()


# main features
def translate(
    text: str,
    to: Language = Language.AUTO,
    from_: Language = Language.AUTO,
    driver: Driver = Driver.CHROME,
    timeout: int = TIMEOUT,
) -> str:
    """Translate a text written in a certain language to another.

    Args:
        text: Text to be translated.
        to: Language to which the text is translated.
        from_: Language of the original text.
        driver: Webdriver for interacting with DeepL.
        timeout: Timeout for translation by DeepL.

    Returns:
        Translated text.

    """
    locator = By.CLASS_NAME, TRANSLATION_CLASS
    url = f"{TRANSLATOR_URL}#{from_.name}/{to.name}/{quote(text)}"

    with get_driver(driver) as driver:
        driver.get(url)
        wait = WebDriverWait(driver, timeout)
        elem = wait.until(text_appeared_in_element(locator))
        return elem.text


# helper features
class text_appeared_in_element:
    """An expectation for checking that an element has an empty text."""

    EMPTY: Final[str] = ""

    def __init__(self, locator: Tuple[str, str]) -> None:
        self.locator = locator

    def __call__(self, driver: WebDriver) -> Union[WebElement, bool]:
        elem = driver.find_element(*self.locator)

        if elem.text == self.EMPTY:
            return False
        else:
            return elem


def get_driver(driver: Driver = Driver.CHROME) -> WebDriver:
    """Return a webdriver for interacting with DeepL."""
    if driver == Driver.CHROME:
        options = ChromeOptions()
        options.add_argument("--headless")
        return Chrome(options=options)
    elif driver == Driver.FIREFOX:
        options = FirefoxOptions()
        options.add_argument("--headless")
        return Firefox(options=options)
    elif driver == Driver.EDGE:
        return Edge()
    elif driver == Driver.SAFARI:
        return Safari()
    else:
        raise ValueError(driver)
