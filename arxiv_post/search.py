__all__ = ["search"]


# standard library
from typing import Generator, Optional, Sequence


# dependencies
from arxiv import Search  # type: ignore
from dateparser import parse


# submodules
from .article import Article
from .constants import START_DATE, END_DATE


# constants
ARXIV_DATE_FORMAT = "%Y%m%d%H%M%S"


# runtime functions
def search(
    categories: Optional[Sequence[str]] = None,
    keywords: Optional[Sequence[str]] = None,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> Generator[Article, None, None]:
    """Search for articles in arXiv.

    Args:
        categories: arXiv categories.
        keywords: Keywords of the search.
        start_date: Start date of the search.
        end_date: End date of the search.

    Yields:
        Articles found with given conditions.

    """
    if categories is None:
        categories = []

    if keywords is None:
        keywords = []

    start_date = format_date(start_date)
    end_date = format_date(end_date)

    query = f"submittedDate:[{start_date} TO {end_date}]"

    if categories:
        sub = " OR ".join(f"cat:{cat}" for cat in categories)
        query += f" AND ({sub})"

    if keywords:
        sub = " OR ".join(f'abs:"{kwd}"' for kwd in keywords)
        query += f" AND ({sub})"

    for result in Search(query).results():
        yield Article.from_arxiv_result(result)


def format_date(date_like: str) -> str:
    """Parse and format a date-like string."""
    if (dt := parse(date_like)) is not None:
        return dt.strftime(ARXIV_DATE_FORMAT)

    raise ValueError(f"Could not parse {date_like!r}.")