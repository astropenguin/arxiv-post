__all__ = ["Query"]


# standard library
from datetime import date, datetime, time, timedelta
from dataclasses import dataclass
from typing import Optional, Sequence, Union


# third-party packages
from typing_extensions import Final


# constants
ABS: Final[str] = "abs"
AND: Final[str] = "AND"
CAT: Final[str] = "cat"
DATE: Final[str] = "submittedDate"
DATE_FORMAT: Final[str] = "%Y%m%d%H%M%S"
OR: Final[str] = "OR"
TO: Final[str] = "TO"
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

    @classmethod
    def today(
        cls,
        keywords: Optional[Sequence[str]] = None,
        categories: Optional[Sequence[str]] = None,
    ) -> "Query":
        """Return a query to search for articles published today."""
        return cls.n_days_ago(0, keywords, categories)

    @classmethod
    def yesterday(
        cls,
        keywords: Optional[Sequence[str]] = None,
        categories: Optional[Sequence[str]] = None,
    ) -> "Query":
        """Return a query to search for articles published yesterday."""
        return cls.n_days_ago(1, keywords, categories)

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


# helper features
def get_today() -> datetime:
    """Return a datetime instance to indicate today."""
    return datetime.combine(date.today(), time())
