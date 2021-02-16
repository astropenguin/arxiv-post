# standard library
import asyncio
from dataclasses import dataclass
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Optional,
    TypeVar,
)


# third-party packages
from aiohttp import ClientSession
from typing_extensions import Final, Protocol
from .translate import Translator
from .search import Article


# constants
TIMEOUT: Final[int] = 60
N_CONCURRENT: Final[int] = 10


# type hints
S = TypeVar("S")
T = TypeVar("T")
Payload = Dict[str, str]


class App(Protocol):
    """Protocol that defines application objects."""

    translator: Translator  #: Translator object.
    n_concurrent: int  #: Number of simultaneous post execution.
    timeout: int  #: Timeout for each post execution.

    async def post(self, articles: AsyncIterable[Article]) -> Awaitable:
        """Translate and post articles to somewhere."""
        ...


# data classes
@dataclass
class Slack:
    """Class for posting articles to Slack by incoming webhook."""

    translator: Translator  #: Translator object.
    n_concurrent: int = N_CONCURRENT  #: Number of simultaneous post execution.
    timeout: int = TIMEOUT  #: Timeout for each post execution (in seconds).
    webhook_url: str = ""  #: URL of Slack incoming webhook.

    async def post(self, articles: AsyncIterable[Article]) -> Awaitable[None]:
        """Translate and post articles to Slack."""
        await amap(self._post, articles, self.n_concurrent, self.timeout)

    async def _post(self, article: Article) -> Awaitable[None]:
        """Translate and post an article to Slack."""
        article = await self.translator.translate(article)
        payload = self._to_payload(article)

        async with ClientSession() as client:
            await client.post(self.webhook_url, json=payload)

        await asyncio.sleep(1.0)

    def _to_payload(self, article: Article) -> Payload:
        """Convert article to payload for Slack post."""
        authors_ = ", ".join(article.authors)
        divider = self.divider()

        title = self.header(self.plain_text(article.title))
        authors = self.section(self.mrkdwn(f"*Authors:* {authors_}"))
        summary = self.section(self.mrkdwn(f"*Summary:* {article.summary}"))
        buttons = self.actions(
            elements=[
                self.button(
                    self.plain_text("View arXiv"),
                    url=article.arxiv_url,
                ),
                self.button(
                    self.plain_text("View PDF"),
                    url=article.arxiv_url.replace("abs", "pdf"),
                ),
            ]
        )

        return dict(blocks=[divider, title, authors, summary, buttons, divider])

    def __getattr__(self, type: str) -> Callable[[str], Payload]:
        """Generate a function to create elements of Slack payload."""

        def element(text: Optional[str] = None, **params) -> Payload:
            if text is None:
                return dict(type=type, **params)

            return dict(text=text, type=type, **params)

        return element


# helper functions
async def amap(
    afunc: Callable[[S], Awaitable[T]],
    aiterable: AsyncIterable[S],
    n_concurrent: int = N_CONCURRENT,
    timeout: int = TIMEOUT,
) -> Awaitable[Iterable[T]]:
    """Async map function.

    Args:
        afunc: Coroutine function.
        aiterable: Async iterable that yields args of afunc.
        n_concurrent: Number of concurrent execution.
        timeout: Timeout for each afunc execution (in seconds).

    Returns:
        Generator that yields results of afunc.

    """
    queue_in = asyncio.Queue()
    queue_out = asyncio.Queue()

    # step 1: create consumer coroutines
    async def consume() -> Awaitable[None]:
        async def _consume() -> Awaitable[None]:
            arg = await queue_in.get()
            coro = asyncio.wait_for(afunc(arg), timeout)

            try:
                result = await coro
            except asyncio.TimeoutError as err:
                result = err
            finally:
                await queue_out.put(result)
                queue_in.task_done()

        try:
            while True:
                await _consume()
        except asyncio.CancelledError:
            pass

    consumers = []

    for _ in range(n_concurrent):
        consumer = asyncio.create_task(consume())
        consumers.append(consumer)

    # step 2: create register coroutine
    async def register() -> Awaitable[None]:
        async for arg in aiterable:
            await queue_in.put(arg)

        await queue_in.join()

        for consumer in consumers:
            consumer.cancel()

    # step 3: run coroutines concurrently
    await asyncio.gather(register(), *consumers)

    # step 4: return results as a generator
    def results():
        while not queue_out.empty():
            yield queue_out.get_nowait()

    return results()
