__all__ = ["translate"]


# standard library
from asyncio import gather, sleep, run
from enum import Enum, auto
from logging import getLogger
from textwrap import shorten
from typing import Iterable, List, Protocol, TypeVar, Union


# dependencies
from more_itertools import divide, flatten
from playwright.async_api import Page, async_playwright


# submodules
from .constants import LANGUAGE_FROM, LANGUAGE_TO, N_CONCURRENT, TIMEOUT


# constants
DEEPL_INPUT = "textarea.lmt__source_textarea"
DEEPL_OUTPUT = "#target-dummydiv"
DEEPL_TRANSLATOR = "https://deepl.com/translator"


class Language(Enum):
    """Available languages in the package."""

    AUTO = auto()  #: Auto language detection
    BG = auto()  #: Bulgarian
    CS = auto()  #: Czech
    DA = auto()  #: Danish
    DE = auto()  #: German
    EL = auto()  #: Greek
    EN = auto()  #: English
    ES = auto()  #: Spanish
    ET = auto()  #: Estonian
    FI = auto()  #: Finnish
    FR = auto()  #: French
    HU = auto()  #: Hungarian
    IT = auto()  #: Italian
    JA = auto()  #: Japanese
    LT = auto()  #: Lithuanian
    LV = auto()  #: Latvian
    NL = auto()  #: Dutch
    PL = auto()  #: Polish
    PT = auto()  #: Portuguese
    RO = auto()  #: Romanian
    RU = auto()  #: Russian
    SK = auto()  #: Slovak
    SL = auto()  #: Slovenian
    SV = auto()  #: Swedish
    ZH = auto()  #: Chinese

    @classmethod
    def from_str(cls, string: str) -> "Language":
        """Convert a string to a language."""
        return getattr(cls, string.upper())

    def to_str(self) -> str:
        """Convert a language to a string."""
        return self.name

    def __str__(self) -> str:
        return self.to_str()


# logger
logger = getLogger(__name__)


# type hints
T = TypeVar("T")


class Translatable(Protocol):
    """Type hint for translatable objects."""

    def replace(self: T, original: str, translated: str) -> T:
        ...

    def __str__(self) -> str:
        ...


TL = TypeVar("TL", bound=Translatable)


# runtime functions
def translate(
    translatables: Iterable[TL],
    language_to: Union[Language, str] = LANGUAGE_TO,
    language_from: Union[Language, str] = LANGUAGE_FROM,
    n_concurrent: int = N_CONCURRENT,
    timeout: float = TIMEOUT,
) -> List[TL]:
    """Translate objects written in one language to another.

    Args:
        translatables: Translatable objects.
        language_to: Language of the translated objects.
        language_from: Language of the original objects.
        n_concurrent: Number of concurrent translation.
        timeout: Timeout for translation per object (in seconds).

    Returns:
        Translated objects.

    """
    return run(
        async_translate(
            translatables,
            language_to,
            language_from,
            n_concurrent,
            timeout,
        )
    )


async def async_translate(
    translatables: Iterable[TL],
    language_to: Union[Language, str],
    language_from: Union[Language, str],
    n_concurrent: int,
    timeout: float,
) -> List[TL]:
    """Async version of the translate function."""
    if isinstance(language_to, str):
        language_to = Language.from_str(language_to)

    if isinstance(language_from, str):
        language_from = Language.from_str(language_from)

    if language_from == language_to:
        return list(translatables)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        context.set_default_timeout(1e3 * timeout)

        async def div_translate(tls: Iterable[TL]) -> List[TL]:
            page = await context.new_page()
            url = f"{DEEPL_TRANSLATOR}#{language_from}/{language_to}/"

            try:
                await page.goto(url)
                return [await _translate(tl, page, timeout) for tl in tls]
            finally:
                await page.close()

        try:
            coros = map(div_translate, divide(n_concurrent, translatables))
            return list(flatten(await gather(*coros)))
        finally:
            await browser.close()


async def _translate(translatable: TL, page: Page, timeout: float) -> TL:
    """Translate an object by a translator page."""
    if not (original := str(translatable)):
        return translatable

    await page.fill(DEEPL_INPUT, "")
    await page.fill(DEEPL_INPUT, original)

    for _ in range(int(timeout / 0.5)):
        await sleep(0.5)

        if (content := await page.text_content(DEEPL_OUTPUT)) is None:
            continue

        if not (content := content.strip()):
            continue

        return translatable.replace(original, content)

    logger.warn(f"Failed to translate: {shorten(original, 50)!r}")
    return translatable
