from __future__ import annotations


# standard library
import asyncio
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from typing import AsyncIterable, Awaitable, Iterable, Optional, Sequence, Union


# third-party packages
from aiohttp import ClientSession, TCPConnector
from feedparser import FeedParserDict, parse
from typing_extensions import Final
from .detex import detex


# constants
ARXIV_API: Final[str] = "http://export.arxiv.org/api/query"
DATE_FORMAT: Final[str] = "%Y%m%d%H%M%S"
SECOND: Final[timedelta] = timedelta(seconds=1)
SEPARATOR: Final[str] = "++++++++++"


# data classes
@dataclass
class Article:
    """Article class for storing article information."""

    title: str  #: Title of an article.
    authors: Sequence[str]  #: Author(s) of an article.
    summary: str  #: Summary of an article.
    arxiv_url: str  #: arXiv URL of an article.

    def __post_init__(self) -> None:
        self.title = detex(self.title)
        self.summary = detex(self.summary)

    def replace(self, text: str, translated: str) -> Article:
        """Method necessary to become translatable."""
        title, summary = translated.split(SEPARATOR)
        return replace(self, title=title, summary=summary)

    def __str__(self) -> str:
        """Method necessary to become translatable."""
        return f"{self.title}\n{SEPARATOR}\n{self.summary}"


@dataclass
class Search:
    """Search class for searching for articles in arXiv."""

    date_start: Union[datetime, str]  #: Start date for a search (inclusive).
    date_end: Union[datetime, str]  #: End date for a search (exclusive).
    keywords: Optional[Sequence[str]] = None  #: Keywords for a search.
    categories: Optional[Sequence[str]] = None  #: arXiv categories.
    n_max_articles: int = 1000  #: Maximum number of articles to get.
    n_per_request: int = 100  #: Number of articles to get per request.
    n_concurrent: int = 1  #: Number of simultaneous requests (do not change).

    def __post_init__(self) -> None:
        if not isinstance(self.date_start, datetime):
            self.date_start = datetime.fromisoformat(self.date_start)

        if not isinstance(self.date_end, datetime):
            self.date_end = datetime.fromisoformat(self.date_end)

    @property
    def search_query(self) -> str:
        """Convert to search query for the arXiv API."""
        date_start = self.date_start.strftime(DATE_FORMAT)
        date_end = (self.date_end - SECOND).strftime(DATE_FORMAT)

        query = f"submittedDate:[{date_start} TO {date_end}]"

        if self.categories:
            sub = " OR ".join(f"cat:{cat}" for cat in self.categories)
            query += f" AND ({sub})"

        if self.keywords:
            sub = " OR ".join(f"abs:{kwd}" for kwd in self.keywords)
            query += f" AND ({sub})"

        return query

    def __aiter__(self) -> AsyncIterable[Article]:
        """Search for articles and yield them as article instances."""

        async def search():
            async for entry in self._search():
                yield Article(
                    title=entry.title,
                    authors=[author.name for author in entry.authors],
                    summary=entry.summary,
                    arxiv_url=entry.link,
                )

        return search()

    async def _search(self) -> AsyncIterable[FeedParserDict]:
        """Search for articles and yield them as Atom entries."""
        connector = TCPConnector(limit=self.n_concurrent)

        async with ClientSession(connector=connector) as client:
            requests = list(self._gen_requests(client))

            for request in asyncio.as_completed(requests):
                feed = parse(await request)

                for entry in feed.entries:
                    yield entry

    def _gen_requests(self, client: TCPConnector) -> Iterable[Awaitable]:
        """Generate coroutines to request the arXiv results."""

        async def request(url: str, **params) -> Awaitable[str]:
            async with client.get(url, params=params) as resp:
                return await resp.text()

        for start in range(0, self.n_max_articles, self.n_per_request):
            max_results = min(
                self.n_per_request,
                self.n_max_articles - start,
            )

            yield request(
                ARXIV_API,
                search_query=self.search_query,
                start=start,
                max_results=max_results,
            )


# utility functions
def search(
    date_start: Union[datetime, str],
    date_end: Union[datetime, str],
    keywords: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
    n_max_articles: int = 1000,
    n_per_request: int = 100,
    n_concurrent: int = 1,
) -> Sequence[Article]:
    """Search for articles in arXiv with given conditions.

    Args:
        date_start: Start date for a search (inclusive).
        date_end: End date for a search (exclusive).
        keywords: Keywords for a search.
        categories: arXiv categories.
        n_max_articles: Maximum number of articles to get.
        n_per_request: Number of articles to get per request.
        n_concurrent: Number of simultaneous requests (do not change).

    Returns:
        List of articles found in arXiv.

    """
    search = Search(
        date_start,
        date_end,
        keywords,
        categories,
        n_max_articles,
        n_per_request,
        n_concurrent,
    )

    async def coro() -> Awaitable:
        return [article async for article in search]

    return asyncio.run(coro())
