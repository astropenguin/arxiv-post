__all__ = ["Article", "Search", "search", "search_n_days_ago"]


# standard library
from datetime import date, datetime, time, timedelta
from dataclasses import dataclass, replace
from typing import Iterator, Optional, Sequence, Union


# third-party packages
import arxiv
from typing_extensions import Final
from .detex import detex


# constants
ABS: Final[str] = "abs"
AND: Final[str] = "AND"
ARXIV_URL: Final[str] = "arxiv_url"
AUTHORS: Final[str] = "authors"
CAT: Final[str] = "cat"
DATE: Final[str] = "submittedDate"
DATE_FORMAT: Final[str] = "%Y%m%d%H%M%S"
MAX_ARTICLES: Final[str] = 100
ONE_SECOND = timedelta(seconds=1)
OR: Final[str] = "OR"
SEPARATOR: Final[str] = "++++++++++"
SUMMARY: Final[str] = "summary"
TITLE: Final[str] = "title"
TO: Final[str] = "TO"


# main features
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

    @classmethod
    def from_arxiv_result(cls, result: dict) -> "Article":
        """Return an article from a result of arXiv query."""
        return cls(
            title=result[TITLE],
            authors=result[AUTHORS],
            summary=result[SUMMARY],
            arxiv_url=result[ARXIV_URL],
        )


@dataclass
class Search:
    """Search class for searching for articles in arXiv."""

    date_start: Union[datetime, str]  #: Start date for a search (inclusive).
    date_end: Union[datetime, str]  #: End date for a search (exclusive).
    keywords: Optional[Sequence[str]] = None  #: Keywords for a search.
    categories: Optional[Sequence[str]] = None  #: arXiv categories.
    max_articles: int = MAX_ARTICLES  #: Maximum number of articles to get.

    def __post_init__(self) -> None:
        if not isinstance(self.date_start, datetime):
            self.date_start = datetime.fromisoformat(self.date_start)

        if not isinstance(self.date_end, datetime):
            self.date_end = datetime.fromisoformat(self.date_end)

    @classmethod
    def n_days_ago(
        cls,
        n: int,
        keywords: Optional[Sequence[str]] = None,
        categories: Optional[Sequence[str]] = None,
        max_articles: int = MAX_ARTICLES,
    ) -> "Search":
        """Return search instance for articles published n days ago.

        Args:
            n: Integer to indicate the date to search.
                For example, `n=1` is for articles yesterday.
            keywords: Keywords for a search (e.g., `['galaxy']`).
            categories: arXiv categories (e.g., `['astro-ph.GA']`).
            max_articles: Maximum number of articles to get.

        Returns:
            Search instance with calculated start and end dates.

        """
        today = datetime.combine(date.today(), time())

        return cls(
            date_start=today - timedelta(days=n),
            date_end=today - timedelta(days=n - 1),
            keywords=keywords,
            categories=categories,
            max_articles=max_articles,
        )

    def run(self) -> Iterator[Article]:
        """Run a search and yield articles found in arXiv."""
        results = arxiv.query(
            query=self.arxiv_query,
            max_results=self.max_articles,
            iterative=True,
        )

        for result in results():
            yield Article.from_arxiv_result(result)

    @property
    def arxiv_query(self) -> str:
        """Query string for the arXiv API."""
        date_start = self.date_start.strftime(DATE_FORMAT)
        date_end = (self.date_end - ONE_SECOND).strftime(DATE_FORMAT)

        query = f"{DATE}:[{date_start} {TO} {date_end}]"

        if self.categories:
            sub = f" {OR} ".join(f"{CAT}:{cat}" for cat in self.categories)
            query += f" {AND} ({sub})"

        if self.keywords:
            sub = f" {OR} ".join(f"{ABS}:{kwd}" for kwd in self.keywords)
            query += f" {AND} ({sub})"

        return query


def search(
    date_start: Union[datetime, str],
    date_end: Union[datetime, str],
    keywords: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
    max_articles: int = MAX_ARTICLES,
) -> Sequence[Article]:
    """Search for articles with given conditions in arXiv.

    Args:
        date_start: Start date for a search (inclusive).
        date_end: End date for a search (exclusive).
        keywords: Keywords for a search (e.g., `['galaxy']`).
        categories: arXiv categories (e.g., `['astro-ph.GA']`).
        max_articles: Maximum number of articles to get.

    Returns:
        Articles found by the conditions.

    """
    search = Search(
        date_start=date_start,
        date_end=date_end,
        keywords=keywords,
        categories=categories,
        max_articles=max_articles,
    )

    return list(search.run())


def search_n_days_ago(
    n: int,
    keywords: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
    max_articles: int = MAX_ARTICLES,
) -> Sequence[Article]:
    """Search for articles published n days ago.

    Args:
        n: Integer to indicate the date to search.
            For example, `n=1` is for articles yesterday.
        keywords: Keywords for a search (e.g., `['galaxy']`).
        categories: arXiv categories (e.g., `['astro-ph.GA']`).
        max_articles: Maximum number of articles to get.

    Returns:
        Articles found by the conditions.

    """
    search = Search.n_days_ago(
        n=n,
        keywords=keywords,
        categories=categories,
        max_articles=max_articles,
    )

    return list(search.run())
