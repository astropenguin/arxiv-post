__all__ = ["translate"]


# standard library
import re
from asyncio import gather, sleep, run
from logging import getLogger
from textwrap import shorten
from typing import Iterable, List, Sequence, Protocol, TypeVar, cast


# dependencies
from deepl import AuthorizationException, Language, TextResult, Translator
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
DEEPL_SOURCE_DIV = "data-testid=translator-source-input"
DEEPL_SOURCE_BOX = "role=textbox"
DEEPL_TARGET_DIV = "data-testid=translator-target-input"
DEEPL_TARGET_BOX = "role=textbox"
DEEPL_TRANSLATOR = "https://deepl.com/translator"


# logger
logger = getLogger(__name__)


# type hints
T = TypeVar("T")


class Translatable(Protocol):
    """Type hint for translatable objects."""

    def replace(self: T, original: str, translated: str, /) -> T:
        ...

    def __str__(self) -> str:
        ...


TL = TypeVar("TL", bound=Translatable)


# runtime functions
def translate(
    translatables: Sequence[TL],
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
        deepl_mode: Translation mode (auto, api, browser) of DeepL.
        deepl_api_key: Authentication Key for DeepL API (api-mode only).
        n_concurrent: Number of concurrent translation (browser-mode only).
        timeout: Timeout for translation in seconds (browser-mode only).

    Returns:
        Translated objects.

    """
    if not translatables:
        return list(translatables)

    target_lang = parse_language(target_lang)
    source_lang = parse_language(source_lang)

    if source_lang == target_lang:
        return list(translatables)

    if deepl_mode == "auto":
        deepl_mode = get_deepl_mode(translatables, deepl_api_key)
        logger.debug(f"Selected translation mode of DeepL: {deepl_mode!r}")

    if deepl_mode == "api":
        return translate_by_api(**locals())
    elif deepl_mode == "browser":
        return translate_by_browser(**locals())
    else:
        raise ValueError(f"{deepl_mode!r} is not supported.")


def translate_by_api(
    translatables: Sequence[TL],
    target_lang: str = TARGET_LANG,
    source_lang: str = SOURCE_LANG,
    deepl_api_key: str = "",
    **_,
) -> List[TL]:
    """Translate objects by the DeepL API."""
    deepl = Translator(deepl_api_key)

    sources = list(map(str, translatables))
    results = deepl.translate_text(
        sources,
        target_lang=target_lang,
        source_lang=source_lang,
    )

    results = cast(List[TextResult], results)
    zipped = zip(translatables, sources, results)
    return [tl.replace(src, res.text) for tl, src, res in zipped]


def translate_by_browser(
    translatables: Sequence[TL],
    target_lang: str = TARGET_LANG,
    source_lang: str = SOURCE_LANG,
    n_concurrent: int = N_CONCURRENT,
    timeout: float = TIMEOUT,
    **_,
) -> List[TL]:
    """Translate objects by the DeepL web translator."""
    n_concurrent = min(n_concurrent, len(translatables))
    url = f"{DEEPL_TRANSLATOR}#{source_lang}/{target_lang}/"

    async def main() -> List[TL]:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            context = await browser.new_context()
            context.set_default_timeout(1e3 * timeout)

            async def inner(translatables: Iterable[TL]) -> List[TL]:
                page = await context.new_page()

                try:
                    await page.goto(url)
                    return [
                        await _translate(translatable, page, timeout)
                        for translatable in translatables
                    ]
                finally:
                    await page.close()

            try:
                coros = map(inner, divide(n_concurrent, translatables))
                return list(flatten(await gather(*coros)))
            finally:
                await browser.close()

    return run(main())


async def _translate(translatable: TL, page: Page, timeout: float) -> TL:
    """Translate an object in a page of a browser."""
    if not (source := str(translatable)):
        return translatable

    source_box = page.locator(DEEPL_SOURCE_DIV).locator(DEEPL_SOURCE_BOX)
    target_box = page.locator(DEEPL_TARGET_DIV).locator(DEEPL_TARGET_BOX)

    await source_box.fill("")
    await source_box.fill(source)

    for _ in range(int(timeout / 0.5)):
        await sleep(0.5)

        if (target := await target_box.inner_text()) is None:
            continue

        if not (target := target.strip()):
            continue

        target = re.sub("\n+", "\n", target)

        try:
            return translatable.replace(source, target)
        except ValueError:
            break

    logger.warn(f"Failed to translate: {shorten(source, 50)!r}")
    return translatable


def parse_language(lang: str) -> str:
    """Parse and format a language string."""
    if (lang := lang.lower()) in vars(Language).values():
        return lang

    try:
        return getattr(Language, lang.upper())
    except AttributeError:
        raise ValueError(f"{lang!r} is not supported.")


def get_deepl_mode(translatables: Iterable[TL], deepl_api_key: str) -> DeepLMode:
    """Choose translation mode of DeepL."""
    if not deepl_api_key:
        return "browser"

    try:
        deepl = Translator(deepl_api_key)
        usage = deepl.get_usage().character
    except AuthorizationException:
        return "browser"

    if not (usage.count is None or usage.limit is None):
        rest = usage.limit - usage.count
        logger.debug(f"Number of character(s) left for translation: {rest}")

        if rest < sum(map(len, map(str, translatables))):
            return "browser"

    return "api"
