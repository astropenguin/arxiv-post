__all__ = ["Query"]


# standard library
from datetime import date, datetime, time, timedelta
from dataclasses import dataclass, replace
from typing import Optional, Sequence, Union


# third-party packages
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
class Query:
    """Query class to search for articles in arXiv."""

    start: Union[datetime, str]  #: Start time for search (inclusive).
    end: Union[datetime, str]  #: End time for search (exclusive).
    keywords: Optional[Sequence[str]] = None  #: Keywords for search.
    categories: Optional[Sequence[str]] = None  #: arXiv categories.

    def __post_init__(self) -> None:
        if not isinstance(self.start, datetime):
            self.start = datetime.fromisoformat(self.start)

        if not isinstance(self.end, datetime):
            self.end = datetime.fromisoformat(self.end)

        if self.keywords is None:
            self.keywords = list()

        if self.categories is None:
            self.categories = list()

    def to_arxiv_query(self) -> str:
        """Convert an instance to a query for the arXiv API."""
        start = self.start.strftime(DATE_FORMAT)
        end = (self.end - timedelta(seconds=1)).strftime(DATE_FORMAT)

        query = f"{DATE}:[{start} {TO} {end}]"

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

        query = f"{DATE}:[{start} {TO} {end}]"

        if self.categories:
            subquery = f" {OR} ".join(f"{CAT}:{cat}" for cat in self.categories)
            query += f" {AND} ({subquery})"

        if self.keywords:
            subquery = f" {OR} ".join(f"{ABS}:{kwd}" for kwd in self.keywords)
            query += f" {AND} ({subquery})"

        return query


# helper features
def get_today() -> datetime:
    """Return a datetime instance to indicate today."""
    return datetime.combine(date.today(), time())
