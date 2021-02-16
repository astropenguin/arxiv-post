from __future__ import annotations


# standard library
import asyncio
from dataclasses import dataclass
from enum import auto, Enum
from typing import Awaitable, Union
from urllib.parse import quote


# third-party packages
from pyppeteer import launch
from typing_extensions import Final, Protocol


# constants
DEEPL_URL: Final[str] = "https://www.deepl.com/translator"
JS_FUNC: Final[str] = "element => element.textContent"
SELECTOR: Final[str] = ".lmt__translations_as_text__text_btn"
TIMEOUT: Final[int] = 60


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
    def url(self) -> str:
        """Base URL of translation."""
        return f"{DEEPL_URL}#/{self.lang_from.name}/{self.lang_to.name}"

    async def translate(self, obj: Translatable) -> Awaitable[Translatable]:
        """Translate object written in one language to another."""
        if self.lang_from == self.lang_to:
            return obj

        text = str(obj)
        translated = await self._translate_text(text)
        return obj.replace(text, translated)

    async def _translate_text(self, text: str) -> Awaitable[str]:
        """Translate text written in one language to another."""
        browser = await launch()
        page = await browser.newPage()
        page.setDefaultNavigationTimeout(self.timeout * 1000)
        completion = self._translation_completion(page)

        try:
            await page.goto(f"{self.url}/{quote(text)}")
            return await asyncio.wait_for(completion, self.timeout)
        except asyncio.TimeoutError as err:
            raise type(err)("Translation was timed out.")
        finally:
            await browser.close()

    async def _translation_completion(self, page) -> Awaitable[str]:
        """Wait for completion of translation and return result."""
        translated = ""

        while not translated:
            await asyncio.sleep(1.0)
            element = await page.querySelector(SELECTOR)
            translated = await page.evaluate(JS_FUNC, element)

        return translated


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
