__all__ = ["Language", "translate"]


# standard library
from enum import auto, Enum
from typing import Tuple, Union
from urllib.parse import quote


# third-party packages
from selenium.webdriver import Safari
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait
from typing_extensions import Final


# constants
TIMEOUT: Final[str] = 30
TRANSLATION_CLASS: Final[str] = "lmt__translations_as_text__text_btn"
TRANSLATOR_URL: Final[str] = "https://www.deepl.com/translator"


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
    timeout: int = TIMEOUT,
) -> str:
    """Translate a text written in a certain language to another.

    Args:
        text: Text to be translated.
        to: Language to which the text is translated.
        from_: Language of the original text.
        timeout: Timeout for translation by DeepL.

    Returns:
        Translated text.

    """
    locator = By.CLASS_NAME, TRANSLATION_CLASS
    url = f"{TRANSLATOR_URL}#{from_.name}/{to.name}/{quote(text)}"

    with Safari() as driver:
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
