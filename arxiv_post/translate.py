__all__ = ["translate"]


# standard library
from asyncio import Semaphore, gather, sleep, run
from typing import Awaitable, Callable, Iterable, List, Protocol, TypeVar, Union


# dependencies
from playwright.async_api import Page, TimeoutError, async_playwright


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
        url = f"{DEEPL_TRANSLATOR}#{language_from}/{language_to}/"

        async def run(translatable: U) -> U:
            if not (original := str(translatable)):
                return translatable

            page = await context.new_page()
            page.set_default_timeout(1e3 * timeout)

            try:
                await page.goto(url)
                await page.fill(DEEPL_INPUT, original)
                translated = await get_text(page, DEEPL_OUTPUT, timeout)
                return translatable.replace(original, translated)
            except TimeoutError:
                return translatable
            finally:
                await page.close()

        try:
            return await async_map(run, translatables, n_concurrent)
        finally:
            await browser.close()


async def get_text(page: Page, selector: str, timeout: float) -> str:
    """Get the nonempty text content in a selector of a page."""
    for _ in range(int(timeout / 0.5)):
        if (content := await page.text_content(selector)) is not None:
            if content := content.strip():
                return content

        await sleep(0.5)

    raise TimeoutError("Nonempty text content did not appear.")


async def async_map(
    coro_func: Callable[[S], Awaitable[T]],
    iterables: Iterable[S],
    n_concurrent: int,
) -> List[T]:
    """Async version of map function."""
    sem = Semaphore(n_concurrent)

    async def task(coro: Awaitable[T]) -> T:
        async with sem:
            return await coro

    awaitables = [task(coro_func(elem)) for elem in iterables]
    return list(await gather(*awaitables))
