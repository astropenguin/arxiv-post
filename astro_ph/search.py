from datetime import timezone
from typing import Generator, Optional, Sequence

from arxiv import Search  # type: ignore
from dateparser import parse

from .article import Article
from .constants import START_DATE, END_DATE


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

    for result in Search(query).get():
        yield Article.from_arxiv_result(result)


def format_date(date_like: str) -> str:
    """Parse and format a date-like string (YYYYmmddHHMMSS)."""
    if (dt := parse(date_like)) is None:
        raise ValueError(f"Could not parse: {date_like}")

    return dt.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
