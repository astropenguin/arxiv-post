__all__ = ["translate"]


# standard library
from asyncio import gather, sleep, run
from typing import Iterable, List, Protocol, TypeVar, Union


# dependencies
from more_itertools import divide, flatten
from playwright.async_api import Page, async_playwright


# submodules
from .constants import LANGUAGE_FROM, LANGUAGE_TO, N_CONCURRENT, TIMEOUT, Language


# constants
DEEPL_INPUT = "textarea.lmt__source_textarea"
DEEPL_OUTPUT = "#target-dummydiv"
DEEPL_TRANSLATOR = "https://deepl.com/translator"


# type hints
S = TypeVar("S")
T = TypeVar("T")


class Translatable(Protocol):
    """Type hint for translatable objects."""

    def replace(self: T, original: str, translated: str) -> T:
        ...

    def __str__(self) -> str:
        ...


U = TypeVar("U", bound=Translatable)


# runtime functions
def translate(
    translatables: Iterable[U],
    language_to: Union[Language, str] = LANGUAGE_TO,
    language_from: Union[Language, str] = LANGUAGE_FROM,
    n_concurrent: int = N_CONCURRENT,
    timeout: float = TIMEOUT,
) -> List[U]:
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
    if isinstance(language_to, str):
        language_to = Language.from_str(language_to)

    if isinstance(language_from, str):
        language_from = Language.from_str(language_from)

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
    translatables: Iterable[U],
    language_to: Language,
    language_from: Language,
    n_concurrent: int,
    timeout: float,
) -> List[U]:
    """Async version of the translate function."""
    if language_from == language_to:
        return list(translatables)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        context.set_default_timeout(1e3 * timeout)

        async def div_translate(trs: Iterable[U]) -> List[U]:
            page = await context.new_page()
            url = f"{DEEPL_TRANSLATOR}#{language_from}/{language_to}/"

            try:
                await page.goto(url)
                return [await _translate(tr, page, timeout) for tr in trs]
            finally:
                await page.close()

        try:
            coros = map(div_translate, divide(n_concurrent, translatables))
            return list(flatten(await gather(*coros)))
        finally:
            await browser.close()


async def _translate(translatable: U, page: Page, timeout: float) -> U:
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

    return translatable
