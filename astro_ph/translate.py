from __future__ import annotations


# standard library
import asyncio
from dataclasses import dataclass
from enum import auto, Enum
from logging import getLogger
from typing import Awaitable, Union
from urllib.parse import quote


# third-party packages
from playwright.async_api import async_playwright, TimeoutError
from typing_extensions import Final, Protocol


# constants
DEEPL_URL: Final[str] = "https://www.deepl.com/translator"
SELECTOR = "#target-dummydiv"
TIMEOUT: Final[int] = 60


# module-level logger
logger = getLogger(__name__)


# enums
class Language(Enum):
    """Available languages for translation."""

    AUTO = auto()  #: Auto language detection
    DE = auto()  #: German
    EN = auto()  #: English
    FR = auto()  #: French
    IT = auto()  #: Italian
    JA = auto()  #: Japanese
    ES = auto()  #: Spanish
    NL = auto()  #: Dutch
    PL = auto()  #: Polish
    PT = auto()  #: Portuguese
    RU = auto()  #: Russian
    ZH = auto()  #: Chinese


# type hints
class Translatable(Protocol):
    """Protocol that defines translatable objects."""

    def __str__(self) -> str:
        """Return text to be translated."""
        ...

    def replace(text: str, translated: str) -> Translatable:
        """Replace text with translated one."""
        ...


class Translator(Protocol):
    """Protocol that defines translator objects."""

    lang_from: Union[Language, str]  #: Language of original text.
    lang_to: Union[Language, str]  #: Language for translated text.
    timeout: int  #: Timeout for translation (in seconds).

    async def translate(self, obj: Translatable) -> Awaitable[Translatable]:
        """Translate object written in one language to another."""
        ...


# data classes
@dataclass
class DeepL:
    """DeepL class for translating text."""

    lang_from: Union[Language, str] = Language.AUTO  #: Language of original text.
    lang_to: Union[Language, str] = Language.AUTO  #: Language for translated text.
    timeout: int = TIMEOUT  #: Timeout for translation (in seconds).

    def __post_init__(self) -> None:
        if isinstance(self.lang_from, str):
            self.lang_from = Language[self.lang_from.upper()]

        if isinstance(self.lang_to, str):
            self.lang_to = Language[self.lang_to.upper()]

    @property
    def base_url(self) -> str:
        """Base URL of translation."""
        return f"{DEEPL_URL}#/{self.lang_from.name}/{self.lang_to.name}"

    async def translate(self, obj: Translatable) -> Awaitable[Translatable]:
        """Translate object written in one language to another."""
        if self.lang_from == self.lang_to:
            return obj

        text = str(obj)
        url = f"{self.base_url}/{quote(text)}"
        logger.debug(f"{url:.300}...")

        async with async_playwright() as p:
            browser = await p.chromium.launch()

            page = await browser.new_page()
            page.set_default_timeout(1e3 * self.timeout)

            try:
                await page.goto(url, wait_until="networkidle")
                elem = await page.query_selector(SELECTOR)
                translated = await elem.text_content()
            except TimeoutError as err:
                raise type(err)("Translation was timed out.")
            finally:
                await browser.close()

        return obj.replace(text, translated.strip())


# utility functions
def translate(
    obj: Translatable,
    lang_to: Union[Language, str] = Language.AUTO,
    lang_from: Union[Language, str] = Language.AUTO,
    timeout: int = TIMEOUT,
) -> Translatable:
    """Translate object written in one language to another.

    Args:
        obj: Object whose text is to be translated.
        lang_to: Language for translated text.
        lang_from: Language of original text.
        timeout: Timeout for translation (in seconds).

    Returns:
        Translated object.

    """
    deepl = DeepL(lang_from, lang_to, timeout)
    return asyncio.run(deepl.translate(obj))
