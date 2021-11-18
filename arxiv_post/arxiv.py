__all__ = ["search"]


# standard library
from logging import getLogger
from typing import List, Sequence


# dependencies
from arxiv import Search
from dateparser import parse


# submodules
from .article import Article
from .consts import CATEGORIES, KEYWORDS, START_DATE, END_DATE


# constants
ARXIV_DATE_FORMAT = "%Y%m%d%H%M%S"


# logger
logger = getLogger(__name__)


# runtime functions
def search(
    categories: Sequence[str] = CATEGORIES,
    keywords: Sequence[str] = KEYWORDS,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> List[Article]:
    """Search for articles in arXiv.

    Args:
        categories: arXiv categories.
        keywords: Keywords of the search.
        start_date: Start date of the search.
        end_date: End date of the search.

    Returns:
        Articles found with given conditions.

    """
    start_date = format_date(start_date)
    end_date = format_date(end_date)

    query = f"submittedDate:[{start_date} TO {end_date}]"

    if categories:
        sub = " OR ".join(f"cat:{cat}" for cat in categories)
        query += f" AND ({sub})"

    if keywords:
        sub = " OR ".join(f'abs:"{kwd}"' for kwd in keywords)
        query += f" AND ({sub})"

    logger.debug(f"Searched articles by: {query!r}")
    results = list(Search(query).results())
    logger.debug(f"Number of articles found: {len(results)}")
    return list(map(Article.from_arxiv_result, results))


def format_date(date_like: str) -> str:
    """Parse and format a date-like string."""
    if (dt := parse(date_like)) is not None:
        return dt.strftime(ARXIV_DATE_FORMAT)

    raise ValueError(f"Could not parse {date_like!r}.")
