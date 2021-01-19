__all__ = ["Driver", "Language", "translate"]


# standard library
from enum import auto, Enum
from typing import Union
from urllib.parse import quote


# third-party packages
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver import Edge, Opera, Remote, Safari
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from typing_extensions import Final


# constants
TRANSLATION_ATTR: Final[str] = "textContent"
TRANSLATION_CLASS: Final[str] = "lmt__translations_as_text__text_btn"
TRANSLATION_TIMEOUT: Final[int] = 30
TRANSLATION_URL: Final[str] = "https://www.deepl.com/translator"


# main features
class Driver(Enum):
    """Available webdrivers for translation."""

    CHROME = auto()
    EDGE = auto()
    FIREFOX = auto()
    OPERA = auto()
    REMOTE = auto()
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


def translate(
    text: str,
    lang_to: Language = Language.AUTO,
    lang_from: Language = Language.AUTO,
    driver: Driver = Driver.CHROME,
    timeout: int = TRANSLATION_TIMEOUT,
    **kwargs,
) -> str:
    """Translate a text written in a certain language to another.

    Args:
        text: Text to be translated.
        lang_to: Language to which the text is translated.
        lang_from: Language of the original text.
        driver: Webdriver for interacting with DeepL.
        timeout: Timeout for translation by DeepL.
        kwargs: Keyword arguments for the webdriver.

    Returns:
        Translated text.

    """
    url = f"{TRANSLATION_URL}#{lang_from.name}/{lang_to.name}/{quote(text)}"

    with get_driver(driver, **kwargs) as driver:
        driver.get(url)
        wait = WebDriverWait(driver, timeout)

        return wait.until(translation_is_finished)


# helper features
def translation_is_finished(driver: Driver) -> Union[bool, str]:
    """Return the translated text when it appears in HTML."""
    elem = driver.find_element(By.CLASS_NAME, TRANSLATION_CLASS)
    text = elem.get_attribute(TRANSLATION_ATTR)

    return False if text == "" else text


def get_driver(driver: Driver, **kwargs) -> WebDriver:
    """Return a webdriver for interacting with DeepL."""
    if driver == Driver.CHROME:
        options = ChromeOptions()
        options.headless = True
        return Chrome(options=options, **kwargs)

    if driver == Driver.FIREFOX:
        options = FirefoxOptions()
        options.headless = True
        return Firefox(options=options, **kwargs)

    if driver == Driver.EDGE:
        return Edge(**kwargs)

    if driver == Driver.OPERA:
        return Opera(**kwargs)

    if driver == Driver.REMOTE:
        return Remote(**kwargs)

    if driver == Driver.SAFARI:
        return Safari(**kwargs)

    raise ValueError(driver)
