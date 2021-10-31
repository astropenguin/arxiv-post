__all__ = ["translate"]


# standard library
from asyncio import gather, sleep, run
from logging import getLogger
from textwrap import shorten
from typing import Iterable, List, Protocol, TypeVar


# dependencies
from deepl import Language
from more_itertools import divide, flatten
from playwright.async_api import Page, async_playwright


# submodules
from .consts import (
    SOURCE_LANG,
    TARGET_LANG,
    DEEPL_MODE,
    N_CONCURRENT,
    TIMEOUT,
    DeepLMode,
)


# constants
DEEPL_INPUT = "textarea.lmt__source_textarea"
DEEPL_OUTPUT = "#target-dummydiv"
DEEPL_TRANSLATOR = "https://deepl.com/translator"


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
    target_lang: str = TARGET_LANG,
    source_lang: str = SOURCE_LANG,
    deepl_mode: DeepLMode = DEEPL_MODE,
    deepl_api_key: str = "",
    n_concurrent: int = N_CONCURRENT,
    timeout: float = TIMEOUT,
) -> List[TL]:
    """Translate objects written in one language to another.

    Args:
        translatables: Translatable objects.
        target_lang: Language of the translated objects.
        source_lang: Language of the original objects.
        deepl_mode: Translation mode of DeepL.
        deepl_api_key: Authentication Key for DeepL API.
        n_concurrent: Number of concurrent translation.
        timeout: Timeout for translation per object (in seconds).

    Returns:
        Translated objects.

    """
    target_lang = parse_language(target_lang)
    source_lang = parse_language(source_lang)

    if source_lang == target_lang:
        return list(translatables)

    return run(
        async_translate(
            translatables,
            target_lang,
            source_lang,
            n_concurrent,
            timeout,
        )
    )


def parse_language(lang: str) -> str:
    """Parse and format a language string."""
    if (lang := lang.lower()) in vars(Language).values():
        return lang

    try:
        return getattr(Language, lang.upper())
    except AttributeError:
        raise ValueError(f"{lang!r} is not supported.")


async def async_translate(
    translatables: Iterable[TL],
    target_lang: str,
    source_lang: str,
    n_concurrent: int,
    timeout: float,
) -> List[TL]:
    """Async version of the translate function."""
    if source_lang == target_lang:
        return list(translatables)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        context.set_default_timeout(1e3 * timeout)

        async def div_translate(tls: Iterable[TL]) -> List[TL]:
            page = await context.new_page()
            url = f"{DEEPL_TRANSLATOR}#{source_lang}/{target_lang}/"

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
