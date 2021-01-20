__all__ = ["Article", "Search", "search"]


# standard library
from datetime import date, datetime, time, timedelta
from dataclasses import dataclass, field, replace
from typing import Optional, Sequence, Union


# third-party packages
import arxiv
from typing_extensions import Final
from .deepl import Driver, Language, translate


# constants
ABS: Final[str] = "abs"
AND: Final[str] = "AND"
ARXIV_URL: Final[str] = "arxiv_url"
AUTHORS: Final[str] = "authors"
CAT: Final[str] = "cat"
DATE: Final[str] = "submittedDate"
DATE_FORMAT: Final[str] = "%Y%m%d%H%M%S"
OR: Final[str] = "OR"
SUMMARY: Final[str] = "summary"
TAGS: Final[str] = "tags"
TERM: Final[str] = "term"
TITLE: Final[str] = "title"
TO: Final[str] = "TO"


# main features
@dataclass
class Article:
    """Article class to store an article information."""

    title: str  #: Title of the article.
    authors: Sequence[str]  #: Author(s) of the article.
    summary: str  #: Summary of the article.
    categories: Sequence[str]  #: arXiv categories.
    arxiv_url: str  #: arXiv URL to the article.

    def __post_init__(self) -> None:
        self.title = self.title.replace("\n", " ")
        self.summary = self.summary.replace("\n", " ")

    @classmethod
    def from_arxiv_result(cls, result: dict) -> "Article":
        """Return an article from a result of arXiv query."""
        return cls(
            title=result[TITLE],
            authors=result[AUTHORS],
            summary=result[SUMMARY],
            categories=[tag[TERM] for tag in result[TAGS]],
            arxiv_url=result[ARXIV_URL],
        )

    def translate(
        self,
        lang_to: Language = Language.AUTO,
        lang_from: Language = Language.AUTO,
        driver: Driver = Driver.CHROME,
    ) -> "Article":
        """Return an article whose title and summary are translated."""
        title = translate(self.title, lang_to, lang_from, driver)
        summary = translate(self.summary, lang_to, lang_from, driver)
        return replace(self, title=title, summary=summary)


@dataclass
class Search:
    """Search class to search for articles in arXiv."""

    date_start: Union[datetime, str]  #: Start date for a search (inclusive).
    date_end: Union[datetime, str]  #: End date for a search (exclusive).
    keywords: Sequence[str] = field(default_factory=list)  #: Keywords for a search.
    categories: Sequence[str] = field(default_factory=list)  #: arXiv categories.

    def __post_init__(self) -> None:
        if not isinstance(self.date_start, datetime):
            self.date_start = datetime.fromisoformat(self.date_start)

        if not isinstance(self.date_end, datetime):
            self.date_end = datetime.fromisoformat(self.date_end)

    def run(self) -> Sequence[Article]:
        """Run a search and return articles found in arXiv."""
        results = arxiv.query(self.to_arxiv_query())
        return [Article.from_arxiv_result(result) for result in results]

    def to_arxiv_query(self) -> str:
        """Convert an instance to a query for the arXiv API."""
        date_start = self.date_start.strftime(DATE_FORMAT)
        date_end = (self.date_end - timedelta(seconds=1)).strftime(DATE_FORMAT)

        query = f"{DATE}:[{date_start} {TO} {date_end}]"

        if self.categories:
            subquery = f" {OR} ".join(f"{CAT}:{cat}" for cat in self.categories)
            query += f" {AND} ({subquery})"

        if self.keywords:
            subquery = f" {OR} ".join(f"{ABS}:{kwd}" for kwd in self.keywords)
            query += f" {AND} ({subquery})"

        return query

    @classmethod
    def n_days_ago(
        cls,
        n: int,
        keywords: Optional[Sequence[str]] = None,
        categories: Optional[Sequence[str]] = None,
    ) -> "Query":
        """Return a query to search for articles published n days ago."""
        return cls(
            start=get_today() - timedelta(days=n),
            end=get_today() - timedelta(days=n - 1),
            keywords=keywords,
            categories=categories,
        )


def search(
    n_days_ago: int,
    keywords: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
) -> Sequence[Article]:
    """Search for articles with given keywords and categories in arXiv.

    Args:
        n_days_ago: Integer to indicate a search range of past.
        keywords: Keywords used for search (e.g., 'galaxy').
        categories: arXiv categories (e.g., 'astro-ph.GA').

    Returns:
        Sequence of articles found in arXiv.

    """
    query = Query.n_days_ago(n_days_ago, keywords, categories)
    results = arxiv.query(query.to_arxiv_query())

    return [Article.from_arxiv_result(result) for result in results]


# helper features
def get_today() -> datetime:
    """Return a datetime instance to indicate today."""
    return datetime.combine(date.today(), time())
